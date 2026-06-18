from __future__ import annotations
from pathlib import Path
from typing import Optional

from ..config import MATERIAL_DIR, MATERIAL_TYPES
from ..storage import write_markdown, timestamp_id
from ..parsers import read_external_file


def ingest_command(
    material_type: str,
    title: str,
    file: Optional[str] = None,
    text: Optional[str] = None,
    note: str = "",
    tags: str = "",
) -> str:
    """Import a material into the system."""
    # Validate type
    if material_type not in MATERIAL_TYPES:
        valid = ", ".join(MATERIAL_TYPES.keys())
        return f"不支持的类型：{material_type}\n可用类型：{valid}"

    # Read content
    content = ""
    source_path = ""
    if file:
        p = Path(file)
        try:
            content = read_external_file(p)
        except (ValueError, FileNotFoundError, OSError) as e:
            return f"文件读取失败: {e}"
        # Store only filename, not full path (M4 fix)
        source_path = p.name
    elif text:
        content = text
    else:
        return "请提供 --file 或 --text 参数。"

    # Content safety scan (T10 fix)
    from ..llm import sanitize_user_input
    safe_content = sanitize_user_input(content)
    content_modified = safe_content != content
    content = safe_content

    # Generate ID and path
    material_id = timestamp_id("material")
    type_dir = MATERIAL_DIR / MATERIAL_TYPES[material_type]
    out_path = type_dir / f"{material_id}.md"

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # Write
    frontmatter = {
        "id": material_id,
        "type": material_type,
        "title": title,
        "source": source_path,
        "tags": tag_list,
        "note": note,
        "source_path": source_path,
    }
    write_markdown(out_path, frontmatter, content)

    lines = [
        "已导入资料：",
        f"  - ID: {material_id}",
        f"  - 路径: {out_path}",
    ]
    if content_modified:
        lines.append("  - 安全扫描：已自动过滤潜在注入内容")
    lines.extend([
        "",
        "下一步建议：",
        f'  skill-forge distill --material {material_id} --problem "要解决的问题"',
        f"  skill-forge inspect --file {out_path} --type auto",
    ])
    return "\n".join(lines)
