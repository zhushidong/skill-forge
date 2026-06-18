"""Review command with actionable update suggestions and structured scoring.

Review scores are STRUCTURED (YAML), not LLM text.
Scores are parsed from LLM output and stored in front matter.
"""
from __future__ import annotations
from pathlib import Path
import re

from ..config import REVIEWS_DIR, SKILLS_DIR
from ..storage import write_markdown, read_markdown, timestamp_id
from ..parsers import read_external_file
from ..templates import render_template
from ..llm import run_llm
from ..skill_manager import find_skill, increment_field_test, update_skill_status


def _parse_review_scores(llm_output: str) -> dict:
    """Parse structured scores from LLM output.
    
    Expects format like:
    adherence: 75
    outcome: 80
    improvement: 70
    skill_defect: 60
    """
    scores = {
        "adherence": 0,
        "outcome": 0,
        "improvement": 0,
        "skill_defect": 0,
    }
    
    for line in llm_output.split("\n"):
        line = line.strip().lower()
        for key in scores:
            if line.startswith(f"{key}:"):
                try:
                    value = int(line.split(":")[1].strip())
                    scores[key] = max(0, min(100, value))
                except (ValueError, IndexError):
                    pass
    
    avg = sum(scores.values()) / len(scores) if scores else 0
    scores["average"] = round(avg, 1)
    
    return scores


def review_command(file: str, result: str, skill: str = "") -> str:
    """Review a real customer interaction with actionable suggestions."""
    path = Path(file)
    try:
        chatlog = read_external_file(path)
    except (ValueError, FileNotFoundError, OSError) as e:
        return f"文件读取失败: {e}"

    # Find skill content if specified
    skill_content = ""
    skill_path = None
    skill_fm = {}
    if skill:
        skill_path = find_skill(skill)
        if skill_path and skill_path.exists():
            skill_fm, skill_content = read_markdown(skill_path)
        else:
            skill_content = f"（未找到 Skill：{skill}）"

    # Render review template
    prompt = render_template("review.md", {
        "result": result,
        "skill": skill_content or "（未指定）",
        "chatlog": chatlog,
    })

    # Run LLM with structured scoring instruction
    review_prompt = prompt + (
        "\n\n请按以下格式输出评分（0-100分）："
        "\nadherence: <是否遵循Skill步骤的分数>"
        "\noutcome: <最终结果的分数>"
        "\nimprovement: <相比上次进步的分数>"
        "\nskill_defect: <Skill本身缺陷的分数（越低越好）>"
        "\n然后给出分析和建议。"
    )
    llm_result = run_llm(review_prompt)

    # Parse structured scores
    scores = _parse_review_scores(llm_result)
    total_score = scores["average"]

    # Generate actionable update suggestions
    update_suggestions = []
    skill_defects = []
    
    if skill_path and skill_path.exists():
        # Analyze skill defects based on review result
        metrics = skill_fm.get("metrics", {})
        drills = metrics.get("drills", 0)
        field_tests = metrics.get("field_tests", 0)
        wins = metrics.get("wins", 0)
        avg_score = metrics.get("avg_score", 0)
        
        # Check for common defects
        if drills < 3:
            skill_defects.append({
                "type": "insufficient_drills",
                "description": f"演练次数不足（当前{drills}次，建议至少3次）",
                "severity": "medium",
            })
        
        if field_tests > 0 and wins / field_tests < 0.6:
            skill_defects.append({
                "type": "low_win_rate",
                "description": f"胜率低于60%（当前{wins}/{field_tests}）",
                "severity": "high",
            })
        
        if avg_score < 60:
            skill_defects.append({
                "type": "low_avg_score",
                "description": f"平均评分低于60（当前{avg_score:.0f}）",
                "severity": "high",
            })
        
        # Generate specific update suggestions based on result
        if result in ("失败", "流失"):
            update_suggestions.append({
                "type": "add_scenario",
                "description": "补充此失败场景到 applicable_scenarios",
                "action": "在 applicable_scenarios 中添加当前场景描述",
                "priority": "high",
            })
            update_suggestions.append({
                "type": "add_forbidden",
                "description": "记录导致失败的行为到 forbidden_behaviors",
                "action": "在 forbidden_behaviors 中添加失败原因",
                "priority": "high",
            })
        
        if result in ("推进", "成交"):
            update_suggestions.append({
                "type": "document_success",
                "description": "记录成功模式到 strategy",
                "action": "在 strategy.steps 中补充成功的关键步骤",
                "priority": "medium",
            })

    # Save review with suggestions
    review_id = timestamp_id("review")
    out_path = REVIEWS_DIR / f"{review_id}.md"
    frontmatter = {
        "id": review_id,
        "type": "review",
        "result": result,
        "skill_id": skill,
        "source_path": path.name,
        "scores": {
            "adherence": scores["adherence"],
            "outcome": scores["outcome"],
            "improvement": scores["improvement"],
            "skill_defect": scores["skill_defect"],
        },
        "total_score": total_score,
        "skill_defects": skill_defects,
        "update_suggestions": update_suggestions,
    }
    write_markdown(out_path, frontmatter, llm_result)

    # Update skill metrics if skill exists
    metrics_info = ""
    if skill_path and skill_path.exists():
        metrics = increment_field_test(skill_path, result, total_score)
        new_status = update_skill_status(skill_path)
        metrics_info = (
            f"\n  - Skill 指标更新: field_tests={metrics.get('field_tests', 0)}, "
            f"wins={metrics.get('wins', 0)}, losses={metrics.get('losses', 0)}, "
            f"avg_score={metrics.get('avg_score', 0):.0f}"
            f"\n  - Skill 状态: {new_status}"
        )

    # Format output with actionable suggestions
    lines = [
        "复盘完成：",
        f"  - 路径: {out_path}",
        f"  - 评分: adherence={scores['adherence']}, outcome={scores['outcome']}, "
        f"improvement={scores['improvement']}, skill_defect={scores['skill_defect']}",
        f"  - 总分: {total_score}",
        metrics_info,
        "",
    ]
    
    if skill_defects:
        lines.append("## Skill 缺陷分析\n")
        for defect in skill_defects:
            lines.append(f"- **{defect['type']}** ({defect['severity']}): {defect['description']}")
        lines.append("")
    
    if update_suggestions:
        lines.append("## 可执行更新建议\n")
        for suggestion in update_suggestions:
            lines.append(f"### {suggestion['type']} ({suggestion['priority']})")
            lines.append(f"- 描述: {suggestion['description']}")
            lines.append(f"- 操作: {suggestion['action']}")
            lines.append("")
        lines.append("**下一步:** 执行 `skill-forge propose-update` 生成更新提案，确认后应用。")
    
    lines.extend([
        "",
        "注意：review 不会直接修改 Skill 内容，修改建议需人工确认后执行。",
    ])
    
    return "\n".join(lines)
