"""Recommend command with explanation."""
from __future__ import annotations
from pathlib import Path

from ..config import SKILLS_DIR, RECOMMENDATIONS_DIR
from ..storage import read_markdown, list_markdown_files, timestamp_id, write_markdown, safe_read_file
from ..templates import render_template
from ..llm import run_llm


def recommend_command(file: str, context: str = "") -> str:
    """Recommend next steps based on current chat and available Skills."""
    path = Path(file)
    try:
        chatlog = safe_read_file(path)
    except ValueError as e:
        return f"文件读取失败: {e}"

    # Read all skill front matters
    skill_files = list_markdown_files(SKILLS_DIR)
    skills_info = []
    candidates = []

    for sf in skill_files:
        try:
            fm, _ = read_markdown(sf)
            if not fm:
                continue
            skill_summary = {
                "id": fm.get("id", ""),
                "name": fm.get("name", ""),
                "scenes": fm.get("scenes", []),
                "customer_stages": fm.get("customer_stages", []),
                "customer_types": fm.get("customer_types", []),
                "signals": fm.get("signals", []),
                "status": fm.get("status", "draft"),
                "metrics": fm.get("metrics", {}),
            }
            skills_info.append(skill_summary)

            # Keyword matching with explanation
            score = 0
            matched_signals = []
            matched_scenes = []
            matched_types = []
            
            chat_lower = chatlog.lower()
            context_lower = context.lower()
            
            for signal in skill_summary["signals"]:
                if signal.lower() in chat_lower or signal.lower() in context_lower:
                    score += 2
                    matched_signals.append(signal)
            for scene in skill_summary["scenes"]:
                if scene.lower() in chat_lower or scene.lower() in context_lower:
                    score += 1
                    matched_scenes.append(scene)
            for ct in skill_summary["customer_types"]:
                if ct.lower() in chat_lower or ct.lower() in context_lower:
                    score += 1
                    matched_types.append(ct)
            for cs in skill_summary["customer_stages"]:
                if cs.lower() in chat_lower or cs.lower() in context_lower:
                    score += 1
            
            if score > 0:
                # Calculate confidence based on score and metrics
                metrics = skill_summary.get("metrics", {})
                drills = metrics.get("drills", 0)
                wins = metrics.get("wins", 0)
                field_tests = metrics.get("field_tests", 0)
                
                # Base confidence from matching
                confidence = min(score / 10, 0.7)
                
                # Boost confidence if skill has good track record
                if field_tests > 0:
                    win_rate = wins / field_tests if field_tests > 0 else 0
                    confidence += win_rate * 0.2
                
                # Boost confidence if skill is trained/tested
                if skill_summary["status"] in ("trained", "tested", "mature"):
                    confidence += 0.1
                
                confidence = min(confidence, 0.95)
                
                # Generate risk warnings
                risk_warnings = []
                if not matched_signals:
                    risk_warnings.append("未匹配到明确的客户信号")
                if skill_summary["status"] == "draft":
                    risk_warnings.append("Skill 尚未训练，效果未验证")
                if drills < 3:
                    risk_warnings.append(f"演练次数不足（当前{drills}次，建议至少3次）")
                
                # Generate explanation
                explanation_parts = []
                if matched_signals:
                    explanation_parts.append(f"当前对话命中客户信号：{', '.join(matched_signals)}")
                if matched_scenes:
                    explanation_parts.append(f"匹配场景：{', '.join(matched_scenes)}")
                if matched_types:
                    explanation_parts.append(f"匹配客户类型：{', '.join(matched_types)}")
                if field_tests > 0:
                    win_rate = wins / field_tests if field_tests > 0 else 0
                    explanation_parts.append(f"历史使用成功率：{win_rate:.0%}")
                explanation_parts.append(f"Skill 状态：{skill_summary['status']}")
                
                candidate = {
                    **skill_summary,
                    "score": score,
                    "confidence": round(confidence, 2),
                    "matched_signals": matched_signals,
                    "matched_scenes": matched_scenes,
                    "matched_types": matched_types,
                    "explanation": "\n".join(explanation_parts),
                    "risk_warnings": risk_warnings,
                }
                candidates.append(candidate)
        except Exception:
            continue

    # Sort by score and take top 5
    candidates.sort(key=lambda x: x["score"], reverse=True)
    top_candidates = candidates[:5]

    # Format candidate skills text with explanation
    if top_candidates:
        candidate_text = ""
        for cs in top_candidates:
            candidate_text += f"\n### {cs['name']} (ID: {cs['id']})\n"
            candidate_text += f"- 状态: {cs['status']}\n"
            candidate_text += f"- 相关度: {cs['score']}\n"
            candidate_text += f"- 置信度: {cs['confidence']:.0%}\n"
            candidate_text += f"- 匹配信号: {', '.join(cs['matched_signals']) or '无'}\n"
            candidate_text += f"- 匹配场景: {', '.join(cs['matched_scenes']) or '无'}\n"
            candidate_text += f"\n**推荐原因：**\n{cs['explanation']}\n"
            if cs['risk_warnings']:
                candidate_text += f"\n**风险提醒：**\n"
                for warning in cs['risk_warnings']:
                    candidate_text += f"- {warning}\n"
    else:
        candidate_text = "（暂无匹配的本地 Skill）"

    # Render recommend template
    prompt = render_template("recommend.md", {
        "context": context or "（未提供背景信息）",
        "chatlog": chatlog,
        "candidate_skills": candidate_text,
    })

    # Run LLM
    result = run_llm(prompt)

    # Save recommendation with explanation
    rec_id = timestamp_id("recommend")
    out_path = RECOMMENDATIONS_DIR / f"{rec_id}.md"
    
    # Build frontmatter with explanation
    frontmatter = {
        "id": rec_id,
        "type": "recommendation",
        "source_path": path.name,
        "matched_skills": [
            {
                "skill_id": cs["id"],
                "skill_name": cs["name"],
                "relevance": cs["score"],
                "confidence": cs["confidence"],
                "explanation": cs["explanation"],
                "risk_warnings": cs["risk_warnings"],
            }
            for cs in top_candidates
        ],
    }
    write_markdown(out_path, frontmatter, result)

    # Format output with explanation
    lines = [
        "推荐完成：",
        f"  - 路径: {out_path}",
        "",
    ]
    
    if top_candidates:
        lines.append("## 推荐结果\n")
        for i, cs in enumerate(top_candidates, 1):
            lines.append(f"### {i}. {cs['name']}")
            lines.append(f"- 置信度: {cs['confidence']:.0%}")
            lines.append(f"- 推荐原因:")
            for exp_line in cs['explanation'].split('\n'):
                lines.append(f"  {exp_line}")
            if cs['risk_warnings']:
                lines.append(f"- 风险提醒:")
                for warning in cs['risk_warnings']:
                    lines.append(f"  - {warning}")
            lines.append("")
    else:
        lines.append("未找到匹配的 Skill。")
    
    lines.extend(["", result])
    
    return "\n".join(lines)
