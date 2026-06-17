from __future__ import annotations
from pathlib import Path

from ..config import SKILLS_DIR
from ..storage import write_markdown, timestamp_id, safe_read_file
from ..parsers import parse_external_file
from ..adapters import to_text
from ..templates import render_template
from ..llm import run_llm


def melt_command(
    file: str,
    asset_type: str = "auto",
    problem: str = "",
    target_scene: str = "",
    title: str = "",
) -> str:
    """Melt an external asset into Skill draft(s)."""
    path = Path(file)
    try:
        content = safe_read_file(path)
    except ValueError as e:
        return f"文件读取失败: {e}"

    try:
        parsed = parse_external_file(path, asset_type)
    except ValueError as e:
        return str(e)

    # Convert to unified text
    unified_text = to_text(parsed)

    # Render melt template
    prompt = render_template("melt.md", {
        "asset_type": parsed["type"],
        "problem": problem or "（未指定，由 LLM 判断）",
        "context": target_scene or "（未指定，由 LLM 判断）",
        "content": unified_text,
    })

    # Run LLM
    result = run_llm(prompt)

    # Save result
    melt_id = timestamp_id("melt")
    out_path = SKILLS_DIR / "draft" / f"melt-result-{melt_id}.md"
    frontmatter = {
        "id": melt_id,
        "name": title or f"从 {parsed['title']} 熔炼",
        "version": "0.1.0",
        "status": "draft",
        "source_type": "external_agent",
        "source_path": path.name,  # Only store filename (M4 fix)
    }
    write_markdown(out_path, frontmatter, result)

    lines = [
        "熔炼完成：",
        f"  - 路径: {out_path}",
        f"  - 来源类型: {parsed['type']}",
        "",
        "下一步建议：",
        f"  skill-forge drill --skill {melt_id} --persona \"目标客户类型\" --rounds 5",
    ]
    return "\n".join(lines)
