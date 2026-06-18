from __future__ import annotations
from pathlib import Path

from ..config import IMPORTS_DIR
from ..storage import write_markdown, timestamp_id
from ..parsers import parse_external_file
from ..adapters import to_text
from ..templates import render_template
from ..llm import run_llm


def inspect_command(file: str, asset_type: str = "auto") -> str:
    """Inspect an external asset and identify capabilities for melting."""
    path = Path(file)

    try:
        parsed = parse_external_file(path, asset_type)
    except (ValueError, FileNotFoundError, OSError) as e:
        return f"文件读取失败: {e}"

    # Convert to unified text
    unified_text = to_text(parsed, asset_type=parsed.get("asset_type", asset_type))

    # Render inspect template
    prompt = render_template("inspect.md", {
        "asset_type": parsed["type"],
        "content": unified_text,
    })

    # Run LLM
    result = run_llm(prompt)

    # Save inspect report
    inspect_id = timestamp_id("inspect")
    out_path = IMPORTS_DIR / f"{inspect_id}-inspect.md"
    frontmatter = {
        "id": inspect_id,
        "type": "inspect",
        "source_path": path.name,  # Only store filename (M4 fix)
        "asset_type": parsed["type"],
    }
    write_markdown(out_path, frontmatter, result)

    lines = [
        "检查完成：",
        f"  - 报告路径: {out_path}",
        f"  - 资产类型: {parsed['type']}",
        "",
        "下一步建议：",
        f"  skill-forge melt --file {file} --type {parsed['type']}",
    ]
    return "\n".join(lines)
