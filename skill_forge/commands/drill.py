"""Drill command with structured scoring.

Drill scores are STRUCTURED (YAML), not LLM text.
Scores are parsed from LLM output and stored in front matter.
"""
from __future__ import annotations
from pathlib import Path
import re

from ..config import SKILLS_DIR, DRILLS_DIR
from ..storage import write_markdown, read_markdown, timestamp_id
from ..templates import render_template
from ..llm import run_llm, run_llm_with_history, has_api_key
from ..skill_manager import find_skill, update_skill_metrics, update_skill_status


def _parse_drill_scores(llm_output: str) -> dict:
    """Parse structured scores from LLM output.
    
    Expects format like:
    diagnosis: 75
    response_quality: 70
    next_step_control: 65
    risk_control: 80
    
    Returns dict with scores and average.
    """
    scores = {
        "diagnosis": 0,
        "response_quality": 0,
        "next_step_control": 0,
        "risk_control": 0,
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


def _determine_drill_result(scores: dict) -> str:
    """Determine drill result from scores."""
    avg = scores.get("average", 0)
    if avg >= 80:
        return "success"
    elif avg >= 60:
        return "partial_success"
    else:
        return "failure"


def drill_command(skill: str, persona: str = "", rounds: int = 5, non_interactive: bool = False) -> str:
    """Run a drill session based on a Skill."""
    # Find skill file
    skill_path = find_skill(skill) if not Path(skill).exists() else Path(skill)

    if not skill_path or not skill_path.exists():
        return (
            f"找不到 skill：{skill}\n\n"
            "你可以：\n"
            "1. 检查 data/skills/ 目录\n"
            "2. 使用完整文件路径\n"
            "3. 先运行 skill-forge distill 生成 Skill"
        )

    fm, skill_body = read_markdown(skill_path)

    # Render drill prompt
    base_prompt = render_template("drill.md", {
        "skill": skill_body,
        "persona": persona or "普通客户",
        "rounds": str(rounds),
    })

    # No API Key: output full prompt for manual use
    if not has_api_key():
        drill_id = timestamp_id("drill")
        out_path = DRILLS_DIR / f"{drill_id}.md"
        frontmatter = {
            "id": drill_id,
            "skill_id": skill,
            "persona": persona or "普通客户",
            "rounds": rounds,
            "scores": {"diagnosis": 0, "response_quality": 0, "next_step_control": 0, "risk_control": 0},
            "average_score": 0,
            "result": "",
        }
        write_markdown(out_path, frontmatter, base_prompt)
        lines = [
            "演练模式（无 API Key）：",
            f"  - Prompt 已保存: {out_path}",
            "",
            "请将以下 Prompt 复制到任意大模型中进行演练。",
            f"  - Skill: {skill}",
            f"  - 客户人格: {persona or '普通客户'}",
            f"  - 轮数: {rounds}",
            "",
            "下一步建议：",
            f"  skill-forge review --file <聊天记录文件> --result \"推进\" --skill {skill}",
        ]
        return "\n".join(lines)

    # Interactive drill with API
    print(f"\n{'='*50}")
    print(f"开始演练 - 客户人格：{persona or '普通客户'}，轮数：{rounds}")
    print(f"输入你的回复，输入 'quit' 结束演练。")
    print(f"{'='*50}\n")

    history: list[dict] = []
    dialogue_log = []

    # First call - get customer opening
    opening_prompt = base_prompt + "\n\n请扮演客户，说出你的第一句话。只输出客户说的话。"
    customer_msg = run_llm(opening_prompt)
    print(f"【客户】：{customer_msg}\n")
    dialogue_log.append(f"【客户】：{customer_msg}")
    history.append({"role": "assistant", "content": customer_msg})

    for i in range(rounds):
        try:
            user_input = input(f"【你（第{i+1}/{rounds}轮）】：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n演练结束。")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("演练结束。")
            break

        dialogue_log.append(f"【你】：{user_input}")
        history.append({"role": "user", "content": user_input})

        # Get customer response
        context = base_prompt + "\n\n对话历史：\n" + "\n".join(dialogue_log)
        context += "\n\n请继续扮演客户，回应用户。只输出客户说的话。"
        customer_msg = run_llm_with_history(context, history)
        print(f"【客户】：{customer_msg}\n")
        dialogue_log.append(f"【客户】：{customer_msg}")
        history.append({"role": "assistant", "content": customer_msg})

    # Get structured review from LLM
    print(f"\n{'='*50}")
    print("正在生成复盘...")
    print(f"{'='*50}\n")

    review_prompt = (
        base_prompt
        + "\n\n完整对话：\n"
        + "\n".join(dialogue_log)
        + "\n\n请对演练进行复盘。必须按以下格式输出评分（0-100分）："
        + "\ndiagnosis: <分数>"
        + "\nresponse_quality: <分数>"
        + "\nnext_step_control: <分数>"
        + "\nrisk_control: <分数>"
        + "\n然后给出改进建议。"
    )
    review = run_llm(review_prompt)

    # Parse structured scores
    scores = _parse_drill_scores(review)
    average_score = scores["average"]
    drill_result = _determine_drill_result(scores)

    # Save drill record
    drill_id = timestamp_id("drill")
    out_path = DRILLS_DIR / f"{drill_id}.md"
    full_content = "## 对话记录\n\n" + "\n\n".join(dialogue_log) + "\n\n## 复盘\n\n" + review
    frontmatter = {
        "id": drill_id,
        "skill_id": skill,
        "persona": persona or "普通客户",
        "rounds": rounds,
        "scores": {
            "diagnosis": scores["diagnosis"],
            "response_quality": scores["response_quality"],
            "next_step_control": scores["next_step_control"],
            "risk_control": scores["risk_control"],
        },
        "average_score": average_score,
        "result": drill_result,
    }
    write_markdown(out_path, frontmatter, full_content)

    # Update skill metrics with structured score
    metrics = update_skill_metrics(skill_path, drill_result, average_score)
    new_status = update_skill_status(skill_path)

    lines = [
        f"\n{'='*50}",
        "演练结束。",
        f"  - 记录已保存: {out_path}",
        f"  - 评分: diagnosis={scores['diagnosis']}, response_quality={scores['response_quality']}, "
        f"next_step_control={scores['next_step_control']}, risk_control={scores['risk_control']}",
        f"  - 平均分: {average_score}",
        f"  - 结果: {drill_result}",
        f"  - Skill 指标更新: drills={metrics.get('drills', 0)}, wins={metrics.get('wins', 0)}, losses={metrics.get('losses', 0)}",
        f"  - Skill 状态: {new_status}",
        f"{'='*50}",
        "",
        "下一步建议：",
        f"  skill-forge review --file <聊天记录文件> --result \"推进\" --skill {skill}",
        f"  skill-forge search --query \"{skill}\"",
    ]
    return "\n".join(lines)
