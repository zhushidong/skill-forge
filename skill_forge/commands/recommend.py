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
            }
            skills_info.append(skill_summary)

            # Simple keyword matching
            score = 0
            chat_lower = chatlog.lower()
            context_lower = context.lower()
            for signal in skill_summary["signals"]:
                if signal.lower() in chat_lower or signal.lower() in context_lower:
                    score += 2
            for scene in skill_summary["scenes"]:
                if scene.lower() in chat_lower or scene.lower() in context_lower:
                    score += 1
            for ct in skill_summary["customer_types"]:
                if ct.lower() in chat_lower or ct.lower() in context_lower:
                    score += 1
            for cs in skill_summary["customer_stages"]:
                if cs.lower() in chat_lower or cs.lower() in context_lower:
                    score += 1
            if score > 0:
                candidates.append((score, skill_summary))
        except Exception:
            continue

    # Sort by score and take top 5
    candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = [c[1] for c in candidates[:5]]

    # Format candidate skills text
    if top_candidates:
        candidate_text = ""
        for cs in top_candidates:
            candidate_text += f"\n- {cs['name']} (ID: {cs['id']})\n"
            candidate_text += f"  场景：{', '.join(cs['scenes'])}\n"
            candidate_text += f"  信号：{', '.join(cs['signals'])}\n"
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

    # Save recommendation
    rec_id = timestamp_id("recommend")
    out_path = RECOMMENDATIONS_DIR / f"{rec_id}.md"
    frontmatter = {
        "id": rec_id,
        "type": "recommendation",
        "source_path": path.name,  # Only store filename (M4 fix)
    }
    write_markdown(out_path, frontmatter, result)

    lines = [
        "推荐完成：",
        f"  - 路径: {out_path}",
        "",
        result,
    ]
    return "\n".join(lines)
