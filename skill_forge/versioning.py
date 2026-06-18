"""Version management for Skills.

- Version snapshots: data/skills/versions/<skill-id>/v<version>.md
- History: scan snapshots directory
- Diff: use difflib.unified_diff
- Rollback: create snapshot, restore, record event
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from datetime import datetime
import difflib
import re

import yaml

from .storage import read_markdown, write_markdown, timestamp_id
from .config import SKILLS_DIR


# ── Version Utils ──────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def increment_version(version: str, change_type: str) -> str:
    """Increment semantic version based on change type.
    
    Args:
        version: Current version string (e.g., "1.2.3")
        change_type: "major", "minor", or "patch"
    
    Returns:
        New version string
    """
    parts = version.split(".")
    if len(parts) != 3:
        return "1.0.0"
    
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if change_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif change_type == "minor":
        minor += 1
        patch = 0
    elif change_type == "patch":
        patch += 1
    
    return f"{major}.{minor}.{patch}"


def get_version_history(skill_path: Path) -> list[dict]:
    """Get version history for a skill by scanning snapshots directory.
    
    Returns list of version records sorted by version number.
    """
    fm, body = read_markdown(skill_path)
    skill_id = fm.get("id", "unknown")
    
    versions_dir = SKILLS_DIR / "versions" / skill_id
    history = []
    
    # Scan snapshots directory
    if versions_dir.exists():
        for snapshot in sorted(versions_dir.glob("v*.md")):
            try:
                snap_fm, _ = read_markdown(snapshot)
                version_name = snapshot.stem  # e.g., "v1.0.0"
                history.append({
                    "version": snap_fm.get("version", version_name.lstrip("v")),
                    "change_type": snap_fm.get("change_type", "unknown"),
                    "change_reason": snap_fm.get("change_reason", ""),
                    "changed_by": snap_fm.get("changed_by", ""),
                    "updated_at": snap_fm.get("updated_at", ""),
                    "status": snap_fm.get("status", "draft"),
                    "snapshot_path": str(snapshot),
                })
            except Exception:
                continue
    
    # Add current version
    history.append({
        "version": fm.get("version", "1.0.0"),
        "change_type": fm.get("change_type", "current"),
        "change_reason": fm.get("change_reason", ""),
        "changed_by": fm.get("changed_by", ""),
        "updated_at": fm.get("updated_at", ""),
        "status": fm.get("status", "draft"),
        "snapshot_path": None,
    })
    
    # Sort by version number
    def version_sort_key(v):
        try:
            parts = v["version"].split(".")
            return tuple(int(p) for p in parts)
        except (ValueError, AttributeError):
            return (0, 0, 0)
    
    history.sort(key=version_sort_key)
    return history


def create_version_snapshot(skill_path: Path, new_version: str, change_type: str, 
                           change_reason: str, changed_by: str) -> Path:
    """Create a snapshot of the skill before updating.
    
    Saves to data/skills/versions/<skill-id>/v<version>.md
    """
    fm, body = read_markdown(skill_path)
    
    skill_id = fm.get("id", "unknown")
    old_version = fm.get("version", "1.0.0")
    
    # Create versions directory
    versions_dir = SKILLS_DIR / "versions" / skill_id
    versions_dir.mkdir(parents=True, exist_ok=True)
    
    # Save snapshot with metadata
    snapshot_fm = {
        **fm,
        "version": old_version,
        "change_type": change_type,
        "change_reason": change_reason,
        "changed_by": changed_by,
        "snapshot_created_at": _now_iso(),
    }
    snapshot_path = versions_dir / f"v{old_version}.md"
    write_markdown(snapshot_path, snapshot_fm, body)
    
    return snapshot_path


def compute_diff(old_body: str, new_body: str) -> str:
    """Compute unified diff between two bodies using difflib."""
    old_lines = old_body.splitlines(keepends=True)
    new_lines = new_body.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile="old version",
        tofile="new version",
        lineterm="",
    )
    return "".join(diff)


def _diff_frontmatter(old_fm: dict, new_fm: dict) -> dict:
    """Compute field-level frontmatter differences.

    Returns dict with added, removed, changed keys.
    Nested dicts/lists are compared as serialized YAML strings.
    """
    old_keys = set(old_fm.keys())
    new_keys = set(new_fm.keys())

    def _normalize(value):
        if isinstance(value, (dict, list)):
            try:
                return yaml.safe_dump(value, sort_keys=True, allow_unicode=True)
            except Exception:
                return str(value)
        return str(value)

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = []
    for key in sorted(old_keys & new_keys):
        if _normalize(old_fm[key]) != _normalize(new_fm[key]):
            changed.append({
                "field": key,
                "old": old_fm[key],
                "new": new_fm[key],
            })

    return {"added": added, "removed": removed, "changed": changed}


def _parse_sections(body: str) -> dict[str, str]:
    """Parse markdown body into header -> content sections.

    Returns ordered dict mapping header title to section content (excluding the header line).
    """
    sections: dict[str, str] = {}
    current_title = "__intro__"
    current_lines: list[str] = []

    for line in body.splitlines(keepends=True):
        if re.match(r"^#{1,6}\s+", line):
            if current_lines:
                sections[current_title] = "".join(current_lines).strip("\n")
            current_title = re.sub(r"^#{1,6}\s+", "", line).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or current_title not in sections:
        sections[current_title] = "".join(current_lines).strip("\n")

    return sections


def _diff_sections(old_body: str, new_body: str) -> dict:
    """Compute section-level body differences.

    Returns dict with added_sections, removed_sections, changed_sections, unchanged_sections.
    """
    old_sections = _parse_sections(old_body)
    new_sections = _parse_sections(new_body)

    old_keys = set(old_sections.keys())
    new_keys = set(new_sections.keys())

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = []
    unchanged = []

    for key in sorted(old_keys & new_keys):
        if old_sections[key] != new_sections[key]:
            line_diff = compute_diff(old_sections[key], new_sections[key])
            changed.append({
                "title": key,
                "diff": line_diff,
                "old_word_count": len(old_sections[key]),
                "new_word_count": len(new_sections[key]),
            })
        else:
            unchanged.append(key)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def diff_versions(skill_path: Path, from_version: str, to_version: str) -> str:
    """Compare two versions of a skill with field-level and section-level detail.

    Returns a formatted diff report.
    """
    fm, body = read_markdown(skill_path)
    skill_id = fm.get("id", "unknown")

    versions_dir = SKILLS_DIR / "versions" / skill_id

    from_path = versions_dir / f"v{from_version}.md"
    to_path = versions_dir / f"v{to_version}.md"

    # If comparing to current version, use the skill file itself
    if to_version == fm.get("version", ""):
        to_path = skill_path

    if not from_path.exists():
        return f"版本 {from_version} 不存在"
    if not to_path.exists():
        return f"版本 {to_version} 不存在"

    from_fm, from_body = read_markdown(from_path)
    to_fm, to_body = read_markdown(to_path)

    fm_diff = _diff_frontmatter(from_fm, to_fm)
    sec_diff = _diff_sections(from_body, to_body)
    line_diff = compute_diff(from_body, to_body)

    lines = [f"# 版本对比: v{from_version} → v{to_version}\n"]

    # Frontmatter field diff
    lines.append("## Frontmatter 字段差异\n")
    if not fm_diff["added"] and not fm_diff["removed"] and not fm_diff["changed"]:
        lines.append("Frontmatter 完全相同。\n")
    else:
        if fm_diff["added"]:
            lines.append("### 新增字段")
            for field in fm_diff["added"]:
                lines.append(f"- `+ {field}`")
            lines.append("")
        if fm_diff["removed"]:
            lines.append("### 删除字段")
            for field in fm_diff["removed"]:
                lines.append(f"- `- {field}`")
            lines.append("")
        if fm_diff["changed"]:
            lines.append("### 修改字段")
            for change in fm_diff["changed"]:
                lines.append(f"- `~ {change['field']}`")
                try:
                    old_yaml = yaml.safe_dump(change["old"], allow_unicode=True, sort_keys=True).strip()
                    new_yaml = yaml.safe_dump(change["new"], allow_unicode=True, sort_keys=True).strip()
                except Exception:
                    old_yaml = str(change["old"])
                    new_yaml = str(change["new"])
                lines.append(f"  - 旧值: `{old_yaml}`")
                lines.append(f"  - 新值: `{new_yaml}`")
            lines.append("")

    # Section-level diff
    lines.append("## 章节差异\n")
    if not sec_diff["added"] and not sec_diff["removed"] and not sec_diff["changed"]:
        lines.append("章节结构完全相同。\n")
    else:
        if sec_diff["added"]:
            lines.append("### 新增章节")
            for title in sec_diff["added"]:
                lines.append(f"- `+ {title}`")
            lines.append("")
        if sec_diff["removed"]:
            lines.append("### 删除章节")
            for title in sec_diff["removed"]:
                lines.append(f"- `- {title}`")
            lines.append("")
        if sec_diff["changed"]:
            lines.append("### 修改章节")
            for change in sec_diff["changed"]:
                lines.append(f"- `~ {change['title']}` "
                             f"(字数 {change['old_word_count']} → {change['new_word_count']})")
            lines.append("")
        if sec_diff["unchanged"]:
            lines.append(f"### 未变更章节\n{', '.join(sec_diff['unchanged'])}")
            lines.append("")

    # Full line-level diff
    lines.append("## 全文行级差异\n")
    if line_diff:
        lines.append("```diff")
        lines.append(line_diff)
        lines.append("```")
    else:
        lines.append("全文内容相同。")

    lines.append("\n## 图例")
    lines.append("- `+` 表示新增")
    lines.append("- `-` 表示删除")
    lines.append("- `~` 表示修改")

    return "\n".join(lines)


def rollback_version(skill_path: Path, target_version: str) -> str:
    """Rollback a skill to a previous version.
    
    Steps:
    1. Create snapshot of current version
    2. Load target version
    3. Update skill to target version content
    4. Bump version number
    5. Record rollback event
    """
    fm, body = read_markdown(skill_path)
    skill_id = fm.get("id", "unknown")
    current_version = fm.get("version", "1.0.0")
    
    versions_dir = SKILLS_DIR / "versions" / skill_id
    target_path = versions_dir / f"v{target_version}.md"
    
    if not target_path.exists():
        return f"版本 {target_version} 不存在"
    
    # Load target version
    target_fm, target_body = read_markdown(target_path)
    
    # Create snapshot of current version before rollback
    create_version_snapshot(
        skill_path,
        current_version,
        "rollback",
        f"回滚到 v{target_version}",
        f"rollback-{timestamp_id('rollback')}"
    )
    
    # Update to target version content with new version number
    new_version = increment_version(current_version, "patch")
    fm["version"] = new_version
    fm["parent_version"] = current_version
    fm["change_type"] = "rollback"
    fm["change_reason"] = f"回滚到 v{target_version}"
    fm["changed_by"] = f"rollback-{timestamp_id('rollback')}"
    fm["updated_at"] = _now_iso()
    
    write_markdown(skill_path, fm, target_body)

    return f"已回滚到 v{target_version}，新版本号: v{new_version}"
