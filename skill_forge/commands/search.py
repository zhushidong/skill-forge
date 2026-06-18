"""Search command: multi-dimensional skill search."""
from __future__ import annotations
import json as json_lib

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .. import storage
from ..config import SKILLS_DIR

console = Console()


def _parse_list_arg(val: str) -> list[str]:
    """Parse comma-separated string into list."""
    if not val:
        return []
    return [p.strip() for p in val.split(",") if p.strip()]


def _match_intersect(skill_vals: list, query_vals: list[str]) -> list[str]:
    """Check if any query value is substring of any skill value."""
    if not query_vals:
        return []
    skill_lower = [str(v).lower() for v in (skill_vals or [])]
    return [q for q in query_vals if any(q.lower() in sv for sv in skill_lower)]


def _fmt_score(score: float) -> str:
    """Format score."""
    if score == int(score):
        return str(int(score))
    return f"{score:.1f}"


def search_command(
    query: str = "",
    scene: str = "",
    signal: str = "",
    customer_type: str = "",
    stage: str = "",
    status: str = "",
    limit: int = 20,
    include_superseded: bool = False,
    json_output: bool = False,
) -> str:
    """Search skills by multiple dimensions."""
    keywords = _parse_list_arg(query)
    scenes_q = _parse_list_arg(scene)
    signals_q = _parse_list_arg(signal)
    ctypes_q = _parse_list_arg(customer_type)
    stages_q = _parse_list_arg(stage)
    status_q = status.strip().lower() if status else ""

    all_files = storage.all_skill_files()
    scanned = len(all_files)
    candidates = []

    for sf in all_files:
        try:
            fm, body = storage.read_markdown(sf)
        except Exception:
            continue

        fm = fm or {}
        skill_status = str(fm.get("status", "")).lower()
        skill_signals = fm.get("customer_signals", []) or fm.get("signals", []) or []
        skill_scenes = fm.get("applicable_scenarios", []) or fm.get("scenes", []) or []
        skill_ctypes = fm.get("customer_types", []) or []
        skill_stages = fm.get("customer_stages", []) or []
        skill_name = str(fm.get("name", ""))
        metrics = fm.get("metrics", {}) or {}
        wins = int(metrics.get("wins", 0) or 0)
        losses = int(metrics.get("losses", 0) or 0)
        field_tests = int(metrics.get("field_tests", 0) or 0)
        superseded_by = fm.get("superseded_by", "")

        # Hide superseded by default
        if superseded_by and not include_superseded and status_q != "retired":
            continue

        # Status filter
        if status_q and skill_status != status_q:
            continue

        # List filters (AND)
        hit_signals = _match_intersect(skill_signals, signals_q)
        if signals_q and not hit_signals:
            continue

        hit_scenes = _match_intersect(skill_scenes, scenes_q)
        if scenes_q and not hit_scenes:
            continue

        hit_ctypes = _match_intersect(skill_ctypes, ctypes_q)
        if ctypes_q and not hit_ctypes:
            continue

        hit_stages = _match_intersect(skill_stages, stages_q)
        if stages_q and not hit_stages:
            continue

        # Keyword filter (OR union across name+body)
        hit_keywords = []
        if keywords:
            text_lower = (skill_name + "\n" + body).lower()
            hit_keywords = [kw for kw in keywords if kw.lower() in text_lower]
            if not hit_keywords:
                continue

        # Score
        score = 0.0
        score += 3 * len(hit_signals)
        score += 2 * len(hit_scenes)
        score += 2 * len(hit_ctypes)
        score += 1 * len(hit_stages)
        score += 1 * len(hit_keywords)
        if skill_status == "mature":
            score += 2
        elif skill_status == "tested":
            score += 1
        score += 0.5 * wins

        candidates.append({
            "id": fm.get("id", sf.stem),
            "name": skill_name,
            "status": skill_status or "draft",
            "version": str(fm.get("version", "")),
            "score": score,
            "path": str(sf),
            "signals": [str(s) for s in skill_signals],
            "scenes": [str(s) for s in skill_scenes],
            "wins": wins,
            "losses": losses,
            "field_tests": field_tests,
        })

    candidates.sort(key=lambda x: (-x["score"], x["name"]))
    matched = candidates[:limit]

    if json_output:
        out = [
            {
                "id": c["id"],
                "name": c["name"],
                "status": c["status"],
                "version": c["version"],
                "score": c["score"],
                "path": c["path"],
                "signals": c["signals"],
                "scenes": c["scenes"],
            }
            for c in matched
        ]
        return json_lib.dumps(out, ensure_ascii=False, indent=2)

    lines = [f"找到 {len(matched)} 个匹配 Skill（共扫描 {scanned} 个）\n"]

    cond_lines = []
    if keywords:
        cond_lines.append(f"关键词: {', '.join(keywords)}")
    if scenes_q:
        cond_lines.append(f"场景: {', '.join(scenes_q)}")
    if signals_q:
        cond_lines.append(f"信号: {', '.join(signals_q)}")
    if ctypes_q:
        cond_lines.append(f"客户类型: {', '.join(ctypes_q)}")
    if stages_q:
        cond_lines.append(f"客户阶段: {', '.join(stages_q)}")
    if status_q:
        cond_lines.append(f"状态: {status_q}")
    if include_superseded:
        cond_lines.append("包含被取代版本: 是")

    if cond_lines:
        lines.append("搜索条件：")
        for cl in cond_lines:
            lines.append(f"  {cl}")
        lines.append("")

    if not matched:
        lines.append("未找到匹配的 Skill。")
        lines.append("")
        lines.append("建议：")
        lines.append("  - 尝试放宽条件")
        lines.append("  - 用 skill-forge distill 创建新 Skill")
        return "\n".join(lines)

    for i, c in enumerate(matched, 1):
        record = f"{c['wins']}胜{c['losses']}负" if c["field_tests"] > 0 else "暂无实战"
        signals_str = ", ".join(c["signals"][:3]) if c["signals"] else "—"
        lines.append(f"  {i}. [{c['status']}] {c['name']} (匹配分: {_fmt_score(c['score'])})")
        lines.append(f"     ID: {c['id']}  版本: {c['version']}")
        lines.append(f"     战绩: {record}  信号: {signals_str}")
        lines.append(f"     路径: {c['path']}")
        lines.append("")

    first = matched[0]
    lines.append(f"详情用: skill-forge drill --skill {first['id']} 或查看文件: {first['path']}")
    return "\n".join(lines)
