"""Shared promotion engine: metrics writeback and status promotion logic.

Used by drill / review / field_log / promote to avoid scattered rules.

Auto-promotion thresholds:
  draft    -> trained : drills >= 2
  trained  -> tested  : wins >= 2
  tested   -> mature  : wins >= 5 AND losses < wins * 0.3
  retired  : manual only

Valid status order:
  draft < trained < tested < mature   ;   retired is terminal
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .. import config, storage
from ..models import now_iso

# Status order (retired handled separately)
_STATUS_ORDER = ["draft", "trained", "tested", "mature"]
_ALL_STATUSES = _STATUS_ORDER + ["retired"]

# Auto-promotion rules
_AUTO_PROMOTE_RULES: dict[str, dict[str, Any]] = {
    "draft": {"to": "trained", "check": lambda m: m.get("drills", 0) >= 2},
    "trained": {"to": "tested", "check": lambda m: m.get("wins", 0) >= 2},
    "tested": {
        "to": "mature",
        "check": lambda m: m.get("wins", 0) >= 5
        and m.get("losses", 0) < m.get("wins", 0) * 0.3,
    },
}

# Result classification
WIN_RESULTS = {"成交", "推进"}
LOSS_RESULTS = {"搁置", "失败", "流失", "停滞"}


def resolve_skill_file(target: str) -> Path | None:
    """Find skill by path or ID."""
    p = Path(target)
    if p.exists() and p.is_file():
        return p
    return storage.find_by_id(config.DATA_DIR / "skills", target)


def read_skill(path: Path) -> tuple[dict, str]:
    """Read skill file, unified entry point."""
    return storage.read_markdown(path)


def bump_metric(metrics: dict, key: str, delta: int = 1) -> dict:
    """Safely increment a metric key."""
    new_m = dict(metrics) if isinstance(metrics, dict) else {}
    new_m[key] = int(new_m.get(key, 0) or 0) + delta
    return new_m


def apply_result_to_metrics(metrics: dict, result: str) -> tuple[dict, str]:
    """Update metrics based on review/field-log result.
    
    Returns (new_metrics, side) where side in {"win", "loss", "neutral"}.
    """
    result = (result or "").strip()
    new_m = bump_metric(metrics, "field_tests", 1)
    if result in WIN_RESULTS:
        new_m = bump_metric(new_m, "wins", 1)
        return new_m, "win"
    if result in LOSS_RESULTS:
        new_m = bump_metric(new_m, "losses", 1)
        return new_m, "loss"
    return new_m, "neutral"


def _status_dir_of(skill_path: Path) -> str | None:
    """Extract status directory from skill file path."""
    try:
        rel = skill_path.relative_to(config.DATA_DIR / "skills")
    except ValueError:
        return None
    if not rel.parts:
        return None
    return rel.parts[0]


def _target_path_for_status(status: str, filename: str) -> Path:
    """Get target file path for a given status."""
    subdir = config.SKILL_STATUS_DIR.get(status, status)
    return config.DATA_DIR / "skills" / subdir / filename


def move_skill_file(old_path: Path, new_status: str) -> Path:
    """Move skill file to new status directory.
    
    If skill is not in data/skills/<status>/ structure, keep in place.
    """
    old_status_dir = _status_dir_of(old_path)
    if old_status_dir is None:
        return old_path

    new_path = _target_path_for_status(new_status, old_path.name)
    if new_path == old_path:
        return old_path

    new_path.parent.mkdir(parents=True, exist_ok=True)
    # Read old content -> write new file -> delete old file
    content = old_path.read_text(encoding="utf-8")
    new_path.write_text(content, encoding="utf-8")
    old_path.unlink()
    return new_path


def write_back_skill(
    skill_path: Path,
    fm: dict,
    body: str,
    *,
    update_timestamp: bool = True,
) -> Path:
    """Write back skill file with optional timestamp update."""
    if update_timestamp:
        fm["updated_at"] = now_iso()
    storage.write_markdown(skill_path, fm, body)
    return skill_path


def check_auto_promote(status: str, metrics: dict) -> str | None:
    """Check if auto-promotion conditions are met, return new status or None."""
    rule = _AUTO_PROMOTE_RULES.get(status)
    if not rule:
        return None
    try:
        if rule["check"](metrics or {}):
            return rule["to"]
    except Exception:
        return None
    return None


def promote_skill_after_metric_change(
    skill_path: Path,
    fm: dict,
    body: str,
) -> tuple[Path, str | None]:
    """After metrics change, check auto-promotion.
    
    If conditions met: update status, move file, write back.
    Returns (new_path or original_path, new_status or None).
    """
    current_status = fm.get("status", "draft")
    new_status = check_auto_promote(current_status, fm.get("metrics") or {})
    if not new_status:
        write_back_skill(skill_path, fm, body)
        return skill_path, None

    fm["status"] = new_status
    write_back_skill(skill_path, fm, body)
    new_path = move_skill_file(skill_path, new_status)
    return new_path, new_status


def validate_manual_promote(current: str, target: str) -> tuple[bool, str]:
    """Validate manual promotion path.
    
    Returns (ok, reason).
    """
    if target not in _ALL_STATUSES:
        return False, f"Unknown target status: {target} (valid: {', '.join(_ALL_STATUSES)})"
    if current not in _ALL_STATUSES:
        return False, f"Unknown current status: {current}"

    if target == current:
        return False, f"Already at status {current}"

    if target == "retired":
        return True, ""

    if current == "retired":
        return False, "retired is terminal; create a new Skill instead"

    try:
        ci = _STATUS_ORDER.index(current)
        ti = _STATUS_ORDER.index(target)
    except ValueError:
        return False, "Invalid status"
    if ti != ci + 1:
        if ti <= ci:
            return False, f"Cannot demote: {current} -> {target}"
        return False, (
            f"Cannot skip levels: {current} -> {target}, "
            f"promote step by step (next: {_STATUS_ORDER[ci+1]})"
        )
    return True, ""


def append_version_record(body: str, line: str) -> str:
    """Append a line to the version log section in body."""
    section_header = "## 版本记录"
    if section_header in body:
        idx = body.index(section_header)
        head = body[:idx]
        tail = body[idx:]
        return head + tail.rstrip() + f"\n- {line}\n"
    return body.rstrip() + f"\n\n{section_header}\n\n- {line}\n"
