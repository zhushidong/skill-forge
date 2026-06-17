from __future__ import annotations
from pathlib import Path
from typing import Optional

from .config import SKILLS_DIR
from .storage import read_markdown, write_markdown, list_markdown_files, find_by_id


def update_skill_metrics(skill_path: Path, drill_result: str = "") -> dict:
    """Update skill metrics after a drill. Returns updated metrics."""
    fm, body = read_markdown(skill_path)
    metrics = fm.get("metrics", {"drills": 0, "field_tests": 0, "wins": 0, "losses": 0})

    # Ensure all keys exist
    for key in ("drills", "field_tests", "wins", "losses"):
        if key not in metrics:
            metrics[key] = 0

    metrics["drills"] = metrics.get("drills", 0) + 1

    # Determine win/loss from result
    result_lower = drill_result.lower() if drill_result else ""
    if any(w in result_lower for w in ("成功", "成交", "推进", "win")):
        metrics["wins"] = metrics.get("wins", 0) + 1
    elif any(w in result_lower for w in ("失败", "流失", "loss")):
        metrics["losses"] = metrics.get("losses", 0) + 1

    fm["metrics"] = metrics
    fm["updated_at"] = _now_iso()
    write_markdown(skill_path, fm, body)
    return metrics


def update_skill_status(skill_path: Path) -> str:
    """Auto-update skill status based on metrics. Returns new status."""
    fm, body = read_markdown(skill_path)
    metrics = fm.get("metrics", {"drills": 0, "field_tests": 0, "wins": 0, "losses": 0})
    current_status = fm.get("status", "draft")

    new_status = current_status

    if current_status == "draft" and metrics.get("drills", 0) >= 3:
        new_status = "trained"
    elif current_status == "trained" and metrics.get("field_tests", 0) >= 1:
        new_status = "tested"
    elif current_status == "tested":
        total_field = metrics.get("field_tests", 0)
        wins = metrics.get("wins", 0)
        if total_field >= 5 and total_field > 0 and (wins / total_field) >= 0.6:
            new_status = "mature"

    if new_status != current_status:
        fm["status"] = new_status
        fm["updated_at"] = _now_iso()
        write_markdown(skill_path, fm, body)

    return new_status


def increment_field_test(skill_path: Path, result: str) -> dict:
    """Increment field_test count and update wins/losses based on result."""
    fm, body = read_markdown(skill_path)
    metrics = fm.get("metrics", {"drills": 0, "field_tests": 0, "wins": 0, "losses": 0})

    for key in ("drills", "field_tests", "wins", "losses"):
        if key not in metrics:
            metrics[key] = 0

    metrics["field_tests"] = metrics.get("field_tests", 0) + 1

    result_lower = result.lower() if result else ""
    if any(w in result_lower for w in ("成功", "成交", "推进")):
        metrics["wins"] = metrics.get("wins", 0) + 1
    elif any(w in result_lower for w in ("失败", "流失")):
        metrics["losses"] = metrics.get("losses", 0) + 1

    fm["metrics"] = metrics
    fm["updated_at"] = _now_iso()
    write_markdown(skill_path, fm, body)
    return metrics


def find_skill(skill_id: str) -> Optional[Path]:
    """Find a skill file by ID across all status directories."""
    for status_dir in SKILLS_DIR.iterdir():
        if status_dir.is_dir():
            found = find_by_id(status_dir, skill_id)
            if found:
                return found
    return None


def list_skills(status: str = "") -> list[dict]:
    """List all skills with their front matter. Filter by status if provided."""
    results = []
    dirs = [SKILLS_DIR / s for s in ["draft", "trained", "tested", "mature", "retired"]]
    if status:
        dirs = [SKILLS_DIR / status]

    for d in dirs:
        if not d.exists():
            continue
        for md_file in list_markdown_files(d):
            try:
                fm, _ = read_markdown(md_file)
                if fm:
                    fm["_path"] = str(md_file)
                    results.append(fm)
            except Exception:
                continue
    return results


def search_skills(query: str) -> list[dict]:
    """Search skills by keyword in name, scenes, signals, customer_types."""
    all_skills = list_skills()
    query_lower = query.lower()
    results = []

    for skill in all_skills:
        score = 0
        # Match name
        if query_lower in skill.get("name", "").lower():
            score += 3
        # Match scenes
        for scene in skill.get("scenes", []):
            if query_lower in scene.lower():
                score += 2
        # Match signals
        for signal in skill.get("signals", []):
            if query_lower in signal.lower():
                score += 2
        # Match customer_types
        for ct in skill.get("customer_types", []):
            if query_lower in ct.lower():
                score += 1
        # Match customer_stages
        for cs in skill.get("customer_stages", []):
            if query_lower in cs.lower():
                score += 1
        # Match avoid_when
        for aw in skill.get("avoid_when", []):
            if query_lower in aw.lower():
                score += 1

        if score > 0:
            results.append((score, skill))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


def _now_iso() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
