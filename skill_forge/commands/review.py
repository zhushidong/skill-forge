from __future__ import annotations
from pathlib import Path

from ..config import REVIEWS_DIR, SKILLS_DIR
from ..storage import write_markdown, read_markdown, timestamp_id, safe_read_file
from ..templates import render_template
from ..llm import run_llm
from ..skill_manager import find_skill, increment_field_test, update_skill_status


def review_command(file: str, result: str, skill: str = "") -> str:
    """Review a real customer interaction."""
    path = Path(file)
    try:
        chatlog = safe_read_file(path)
    except ValueError as e:
        return f"文件读取失败: {e}"

    # Find skill content if specified
    skill_content = ""
    skill_path = None
    if skill:
        skill_path = find_skill(skill)
        if skill_path and skill_path.exists():
            _, skill_content = read_markdown(skill_path)
        else:
            skill_content = f"（未找到 Skill：{skill}）"

    # Render review template
    prompt = render_template("review.md", {
        "result": result,
        "skill": skill_content or "（未指定）",
        "chatlog": chatlog,
    })

    # Run LLM
    llm_result = run_llm(prompt)

    # Save review
    review_id = timestamp_id("review")
    out_path = REVIEWS_DIR / f"{review_id}.md"
    frontmatter = {
        "id": review_id,
        "type": "review",
        "result": result,
        "skill_id": skill,
        "source_path": path.name,  # Only store filename (M4 fix)
    }
    write_markdown(out_path, frontmatter, llm_result)

    # Update skill metrics if skill exists
    metrics_info = ""
    if skill_path and skill_path.exists():
        metrics = increment_field_test(skill_path, result)
        new_status = update_skill_status(skill_path)
        metrics_info = (
            f"\n  - Skill 指标更新: field_tests={metrics.get('field_tests', 0)}, "
            f"wins={metrics.get('wins', 0)}, losses={metrics.get('losses', 0)}"
            f"\n  - Skill 状态: {new_status}"
        )

    lines = [
        "复盘完成：",
        f"  - 路径: {out_path}",
        metrics_info,
        "",
        "注意：review 不会直接修改 Skill 内容，修改建议需人工确认后执行。",
    ]
    return "\n".join(lines)
