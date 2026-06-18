"""Recommend command with explanation.

Recommendation is keyword/tag matching + confidence scoring + risk warnings.
Not a vector search system. Not an LLM-based recommendation engine.
It matches customer signals, scenes, and types against local Skills.
"""
from __future__ import annotations
from pathlib import Path

from ..config import SKILLS_DIR, RECOMMENDATIONS_DIR
from ..storage import read_markdown, list_markdown_files, timestamp_id, write_markdown
from ..parsers import read_external_file
from ..templates import render_template
from ..llm import run_llm


def recommend_command(file: str, context: str = "") -> str:
    """Recommend next steps based on current chat and available Skills."""
    path = Path(file)
    try:
        chatlog = read_external_file(path)
    except (ValueError, FileNotFoundError, OSError) as e:
        return f"文件读取失败: {e}"

    # Read all skill front matters
    skill_files = list_markdown_files(SKILLS_DIR)
    candidates = []

    for sf in skill_files:
        try:
            fm, _ = read_markdown(sf)
            if not fm:
                continue
            
            # Extract fields with old/new schema fallback
            skill_id = fm.get("id", "")
            skill_name = fm.get("name", "")
            # New schema: applicable_scenarios, customer_signals
            # Old schema: scenes, signals
            scenes = fm.get("applicable_scenarios", []) or fm.get("scenes", [])
            customer_signals = fm.get("customer_signals", []) or fm.get("signals", [])
            customer_types = fm.get("customer_types", []) or []
            customer_stages = fm.get("customer_stages", []) or []
            # Also match against name and domain keywords
            name_keywords = [w for w in skill_name.split() if len(w) > 1]
            status = fm.get("status", "draft")
            metrics = fm.get("metrics", {})
            
            # Extract metrics with defaults (handle nested or flat)
            drills = metrics.get("drills", 0) if isinstance(metrics, dict) else 0
            field_tests = metrics.get("field_tests", 0) if isinstance(metrics, dict) else 0
            wins = metrics.get("wins", 0) if isinstance(metrics, dict) else 0
            losses = metrics.get("losses", 0) if isinstance(metrics, dict) else 0
            avg_score = metrics.get("avg_score", 0) if isinstance(metrics, dict) else 0

            # Keyword matching with explanation
            score = 0
            matched_signals = []
            matched_scenes = []
            
            chat_lower = chatlog.lower()
            context_lower = context.lower()
            
            for signal in customer_signals:
                if signal.lower() in chat_lower or signal.lower() in context_lower:
                    score += 2
                    matched_signals.append(signal)
            for scene in scenes:
                if scene.lower() in chat_lower or scene.lower() in context_lower:
                    score += 1
                    matched_scenes.append(scene)
            for ctype in customer_types:
                if ctype.lower() in chat_lower or ctype.lower() in context_lower:
                    score += 1
                    matched_scenes.append(f"客户类型: {ctype}")
            for stage in customer_stages:
                if stage.lower() in chat_lower or stage.lower() in context_lower:
                    score += 1
                    matched_scenes.append(f"客户阶段: {stage}")
            # Fallback: match name keywords against chat content
            for kw in name_keywords:
                if kw.lower() in chat_lower or kw.lower() in context_lower:
                    score += 1
                    matched_scenes.append(f"名称关键词: {kw}")
            
            if score > 0:
                # Calculate confidence based on score and metrics
                confidence = min(score / 10, 0.7)
                
                # Boost confidence if skill has good track record
                if field_tests > 0:
                    win_rate = wins / field_tests
                    confidence += win_rate * 0.2
                
                # Boost confidence if skill is trained/tested/mature
                if status in ("trained", "tested", "mature"):
                    confidence += 0.1
                
                confidence = min(confidence, 0.95)
                
                # Generate risk warnings
                risk_warnings = []
                if not matched_signals:
                    risk_warnings.append("未匹配到明确的客户信号")
                if status == "draft":
                    risk_warnings.append("Skill 尚未训练，效果未验证")
                if drills < 3:
                    risk_warnings.append(f"演练次数不足（当前{drills}次，建议至少3次）")
                if field_tests > 0 and wins / field_tests < 0.6:
                    risk_warnings.append(f"胜率低于60%（当前{wins}/{field_tests}）")
                
                # Generate explanation
                explanation_parts = []
                if matched_signals:
                    explanation_parts.append(f"当前对话命中客户信号：{', '.join(matched_signals)}")
                if matched_scenes:
                    explanation_parts.append(f"匹配场景：{', '.join(matched_scenes)}")
                if field_tests > 0:
                    win_rate = wins / field_tests
                    explanation_parts.append(f"历史使用成功率：{win_rate:.0%}")
                explanation_parts.append(f"Skill 状态：{status}")
                if avg_score > 0:
                    explanation_parts.append(f"平均评分：{avg_score:.0f}")
                
                candidate = {
                    "id": skill_id,
                    "name": skill_name,
                    "status": status,
                    "score": score,
                    "confidence": round(confidence, 2),
                    "matched_signals": matched_signals,
                    "matched_scenes": matched_scenes,
                    "explanation": "\n".join(explanation_parts),
                    "risk_warnings": risk_warnings,
                    "metrics": {
                        "drills": drills,
                        "field_tests": field_tests,
                        "wins": wins,
                        "losses": losses,
                        "avg_score": avg_score,
                    },
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
            m = cs['metrics']
            win_rate_str = f"{m['wins']}/{m['field_tests']}" if m['field_tests'] > 0 else "暂无"
            candidate_text += f"- 演练: {m['drills']}次, 实战: {m['field_tests']}次, 胜率: {win_rate_str}\n"
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
