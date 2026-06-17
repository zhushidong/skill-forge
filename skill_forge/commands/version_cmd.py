"""Version management commands."""
from __future__ import annotations
from pathlib import Path

from ..skill_manager import find_skill
from ..versioning import get_version_history, diff_versions, rollback_version, create_version_snapshot


def history_command(skill: str) -> str:
    """Show version history for a skill."""
    skill_path = find_skill(skill) if not Path(skill).exists() else Path(skill)
    
    if not skill_path or not skill_path.exists():
        return (
            f"找不到 skill：{skill}\n\n"
            "你可以：\n"
            "1. 检查 data/skills/ 目录\n"
            "2. 使用完整文件路径\n"
            "3. 先运行 skill-forge distill 生成 Skill"
        )
    
    history = get_version_history(skill_path)
    
    if not history:
        return "没有版本历史记录。"
    
    lines = [f"版本历史：\n"]
    
    for i, record in enumerate(history, 1):
        lines.append(f"  {i}. v{record['version']}")
        lines.append(f"     状态: {record['status']}")
        lines.append(f"     类型: {record['change_type']}")
        if record['change_reason']:
            lines.append(f"     原因: {record['change_reason']}")
        if record['changed_by']:
            lines.append(f"     来源: {record['changed_by']}")
        if record['updated_at']:
            lines.append(f"     时间: {record['updated_at']}")
        lines.append("")
    
    return "\n".join(lines)


def diff_command(skill: str, from_version: str, to_version: str = "current") -> str:
    """Compare two versions of a skill."""
    skill_path = find_skill(skill) if not Path(skill).exists() else Path(skill)
    
    if not skill_path or not skill_path.exists():
        return f"找不到 skill：{skill}"
    
    if to_version == "current":
        from ..storage import read_markdown
        fm, _ = read_markdown(skill_path)
        to_version = fm.get("version", "1.0.0")
    
    return diff_versions(skill_path, from_version, to_version)


def rollback_command(skill: str, to_version: str) -> str:
    """Rollback a skill to a previous version."""
    skill_path = find_skill(skill) if not Path(skill).exists() else Path(skill)
    
    if not skill_path or not skill_path.exists():
        return f"找不到 skill：{skill}"
    
    return rollback_version(skill_path, to_version)
