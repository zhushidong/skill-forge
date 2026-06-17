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

from .storage import read_markdown, write_markdown, list_markdown_files, timestamp_id
from .config import SKILLS_DIR


# ── Version Utils ──────────────────────────────────────────────

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


def diff_versions(skill_path: Path, from_version: str, to_version: str) -> str:
    """Compare two versions of a skill.
    
    Returns a diff string.
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
    
    _, from_body = read_markdown(from_path)
    _, to_body = read_markdown(to_path)
    
    diff = compute_diff(from_body, to_body)
    
    if not diff:
        return f"# 版本对比: v{from_version} → v{to_version}\n\n两个版本内容相同。"
    
    return f"""# 版本对比: v{from_version} → v{to_version}

## 差异

```diff
{diff}
```

## 说明

- `+` 表示新增内容
- `-` 表示删除内容
"""


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


def _now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
