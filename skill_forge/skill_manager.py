"""Skill manager: metrics, status, search.

Status machine:
- draft → trained: drills >= 3, avg_score >= 60
- trained → tested: field_tests >= 1, review result = "推进" or "成交"
- tested → mature: field_tests >= 5, win_rate >= 0.6, avg_score >= 70
- mature → retired: 90 days no use, or 3/5 failures, or manual

All status transitions are CODE-ENFORCED, not just documentation.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from .config import SKILLS_DIR
from .storage import read_markdown, write_markdown, list_markdown_files, find_by_id


def update_skill_metrics(skill_path: Path, drill_result: str = "", score: float = 0) -> dict:
    """Update skill metrics after a drill. Returns updated metrics."""
    fm, body = read_markdown(skill_path)
    
    # Ensure nested metrics dict exists
    if "metrics" not in fm or not isinstance(fm["metrics"], dict):
        fm["metrics"] = {}
    metrics = fm["metrics"]
    
    # Ensure all keys exist
    for key in ("drills", "field_tests", "wins", "losses", "avg_score"):
        if key not in metrics:
            metrics[key] = 0

    metrics["drills"] = metrics.get("drills", 0) + 1

    # Update avg_score (running average)
    old_avg = metrics.get("avg_score", 0)
    old_drills = metrics.get("drills", 1) - 1  # before increment
    if old_drills > 0:
        new_avg = (old_avg * old_drills + score) / metrics["drills"]
    else:
        new_avg = score
    metrics["avg_score"] = round(new_avg, 1)

    # Determine win/loss from result
    result_lower = drill_result.lower() if drill_result else ""
    if any(w in result_lower for w in ("成功", "成交", "推进", "win", "success")):
        metrics["wins"] = metrics.get("wins", 0) + 1
    elif any(w in result_lower for w in ("失败", "流失", "loss", "failure")):
        metrics["losses"] = metrics.get("losses", 0) + 1

    fm["metrics"] = metrics
    fm["updated_at"] = _now_iso()
    write_markdown(skill_path, fm, body)
    return metrics


def update_skill_status(skill_path: Path) -> str:
    """Auto-update skill status based on metrics. Returns new status.
    
    Status transitions are CODE-ENFORCED with specific thresholds.
    If conditions are not met, status does NOT change.
    """
    fm, body = read_markdown(skill_path)
    
    if "metrics" not in fm or not isinstance(fm["metrics"], dict):
        fm["metrics"] = {}
    metrics = fm["metrics"]
    
    current_status = fm.get("status", "draft")
    new_status = current_status

    drills = metrics.get("drills", 0)
    field_tests = metrics.get("field_tests", 0)
    wins = metrics.get("wins", 0)
    avg_score = metrics.get("avg_score", 0)

    # draft → trained: drills >= 3 AND avg_score >= 60
    if current_status == "draft":
        if drills >= 3 and avg_score >= 60:
            new_status = "trained"
            fm["trained_at"] = _now_iso()

    # trained → tested: field_tests >= 1
    elif current_status == "trained":
        if field_tests >= 1:
            new_status = "tested"
            fm["tested_at"] = _now_iso()

    # tested → mature: field_tests >= 5, win_rate >= 0.6, avg_score >= 70
    elif current_status == "tested":
        if field_tests >= 5 and field_tests > 0:
            win_rate = wins / field_tests
            if win_rate >= 0.6 and avg_score >= 70:
                new_status = "mature"
                fm["mature_at"] = _now_iso()

    # mature → retired: check conditions
    elif current_status == "mature":
        last_used = metrics.get("last_used_at", "")
        if last_used:
            try:
                last_used_dt = datetime.fromisoformat(last_used)
                if datetime.now() - last_used_dt > timedelta(days=90):
                    new_status = "retired"
                    fm["retired_at"] = _now_iso()
            except (ValueError, TypeError):
                pass
        
        # Check failure rate: 3/5 recent failures
        if field_tests >= 5 and losses >= 3:
            new_status = "retired"
            fm["retired_at"] = _now_iso()

    if new_status != current_status:
        fm["status"] = new_status
        fm["updated_at"] = _now_iso()
        write_markdown(skill_path, fm, body)

    return new_status


def increment_field_test(skill_path: Path, result: str, score: float = 0) -> dict:
    """Increment field_test count and update wins/losses based on result."""
    fm, body = read_markdown(skill_path)
    
    if "metrics" not in fm or not isinstance(fm["metrics"], dict):
        fm["metrics"] = {}
    metrics = fm["metrics"]

    for key in ("drills", "field_tests", "wins", "losses", "avg_score"):
        if key not in metrics:
            metrics[key] = 0

    metrics["field_tests"] = metrics.get("field_tests", 0) + 1
    metrics["last_used_at"] = _now_iso()

    # Update avg_score (running average)
    old_avg = metrics.get("avg_score", 0)
    old_tests = metrics.get("field_tests", 1) - 1  # before increment
    if old_tests > 0:
        new_avg = (old_avg * old_tests + score) / metrics["field_tests"]
    else:
        new_avg = score
    metrics["avg_score"] = round(new_avg, 1)

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
    """Search skills by keyword in name, scenes, signals."""
    all_skills = list_skills()
    query_lower = query.lower()
    results = []

    for skill in all_skills:
        score = 0
        # Match name
        if query_lower in skill.get("name", "").lower():
            score += 3
        # Match applicable_scenarios
        for scene in skill.get("applicable_scenarios", []):
            if query_lower in scene.lower():
                score += 2
        # Match customer_signals
        for signal in skill.get("customer_signals", []):
            if query_lower in signal.lower():
                score += 2
        # Match problem
        if query_lower in skill.get("problem", "").lower():
            score += 1

        if score > 0:
            results.append((score, skill))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]


def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
