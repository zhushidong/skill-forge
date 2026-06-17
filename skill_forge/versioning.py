"""Version management for Skills."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from datetime import datetime

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
    """Get version history for a skill.
    
    Returns list of version records sorted by version number.
    """
    fm, body = read_markdown(skill_path)
    
    history = [{
        "version": fm.get("version", "1.0.0"),
        "change_type": fm.get("change_type", "initial"),
        "change_reason": fm.get("change_reason", ""),
        "changed_by": fm.get("changed_by", ""),
        "updated_at": fm.get("updated_at", ""),
        "status": fm.get("status", "draft"),
    }]
    
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
    
    # Save snapshot
    snapshot_path = versions_dir / f"v{old_version}.md"
    write_markdown(snapshot_path, fm, body)
    
    return snapshot_path


def compute_diff(old_body: str, new_body: str) -> str:
    """Compute a simple line-by-line diff between two bodies."""
    old_lines = old_body.splitlines()
    new_lines = new_body.splitlines()
    
    diff_lines = []
    max_len = max(len(old_lines), len(new_lines))
    
    for i in range(max_len):
        old_line = old_lines[i] if i < len(old_lines) else None
        new_line = new_lines[i] if i < len(new_lines) else None
        
        if old_line is None:
            diff_lines.append(f"+ {new_line}")
        elif new_line is None:
            diff_lines.append(f"- {old_line}")
        elif old_line != new_line:
            diff_lines.append(f"- {old_line}")
            diff_lines.append(f"+ {new_line}")
    
    return "\n".join(diff_lines)


def diff_versions(skill_path: Path, from_version: str, to_version: str) -> str:
    """Compare two versions of a skill.
    
    Returns a diff string.
    """
    fm, body = read_markdown(skill_path)
    skill_id = fm.get("id", "unknown")
    
    versions_dir = SKILLS_DIR / "versions" / skill_id
    
    from_path = versions_dir / f"v{from_version}.md"
    to_path = versions_dir / f"v{to_version}.md"
    
    if not from_path.exists():
        return f"版本 {from_version} 不存在"
    if not to_path.exists():
        return f"版本 {to_version} 不存在"
    
    _, from_body = read_markdown(from_path)
    _, to_body = read_markdown(to_path)
    
    diff = compute_diff(from_body, to_body)
    
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
    
    Returns success message or error.
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
    
    # Create snapshot of current version
    create_version_snapshot(
        skill_path,
        current_version,
        "rollback",
        f"回滚到 v{target_version}",
        f"rollback-{timestamp_id('rollback')}"
    )
    
    # Update to target version
    new_version = increment_version(current_version, "patch")
    target_fm["version"] = new_version
    target_fm["parent_version"] = current_version
    target_fm["change_type"] = "patch"
    target_fm["change_reason"] = f"回滚到 v{target_version}"
    target_fm["changed_by"] = f"rollback-{timestamp_id('rollback')}"
    target_fm["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    write_markdown(skill_path, target_fm, target_body)
    
    return f"已回滚到 v{target_version}，新版本号: v{new_version}"
