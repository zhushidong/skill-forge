from __future__ import annotations
from ..storage import ensure_workspace, ensure_templates


def init_command(force: bool = False) -> str:
    """Initialize workspace directories and default templates."""
    dirs_created, _ = ensure_workspace()
    files_created = ensure_templates(force=force)

    lines = ["初始化完成！\n"]

    if dirs_created:
        lines.append("已创建目录：")
        for d in dirs_created:
            lines.append(f"  - {d}")
    else:
        lines.append("目录已存在，跳过。")

    if files_created:
        lines.append("\n已创建模板：")
        for f in files_created:
            lines.append(f"  - {f}")
    else:
        lines.append("\n模板已存在，跳过。")

    if force and not files_created:
        lines.append("\n（未发现需要覆盖的模板，如需强制覆盖请确认模板目录存在）")

    lines.append("\n下一步建议：")
    lines.append("  skill-forge ingest --type case --title \"案例标题\" --file ./case.md")

    return "\n".join(lines)
