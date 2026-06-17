from __future__ import annotations

from ..skill_manager import search_skills, list_skills


def search_command(query: str = "", status: str = "") -> str:
    """Search or list skills."""
    if query:
        results = search_skills(query)
        if not results:
            return f"未找到匹配 '{query}' 的 Skill。\n\n你可以：\n1. 尝试其他关键词\n2. 运行 skill-forge search 不带参数查看所有 Skill"
    else:
        results = list_skills(status)
        if not results:
            return "暂无 Skill。你可以运行 skill-forge distill 或 skill-forge melt 生成 Skill。"

    lines = [f"找到 {len(results)} 个 Skill：\n"]

    for i, skill in enumerate(results, 1):
        status_tag = skill.get("status", "draft")
        name = skill.get("name", "未命名")
        sid = skill.get("id", "")
        scenes = ", ".join(skill.get("scenes", [])[:3])
        metrics = skill.get("metrics", {})
        drills = metrics.get("drills", 0)
        wins = metrics.get("wins", 0)

        lines.append(f"  {i}. [{status_tag}] {name}")
        lines.append(f"     ID: {sid}")
        if scenes:
            lines.append(f"     场景: {scenes}")
        lines.append(f"     演练: {drills} 次, 胜: {wins}")
        lines.append("")

    lines.append("查看详情：skill-forge inspect --file <skill-file>")
    return "\n".join(lines)
