from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from .config import (
    DATA_DIR, TEMPLATES_DIR, SAMPLES_DIR, MATERIAL_DIR, SKILLS_DIR, DRILLS_DIR,
    FIELD_LOGS_DIR, REVIEWS_DIR, RECOMMENDATIONS_DIR, IMPORTS_DIR, PROFILES_DIR,
    MATERIAL_TYPES, SKILL_STATUSES,
)


# ── Path Security ──────────────────────────────────────────────

# All allowed base directories (now absolute paths from config.py)
_ALLOWED_BASES = [
    DATA_DIR,
    TEMPLATES_DIR,
    SAMPLES_DIR,
]


def _validate_path(path: Path, allowed_bases: Optional[list[Path]] = None) -> Path:
    """Validate and resolve a path, ensuring it stays within allowed directories.
    
    Raises ValueError if path escapes allowed boundaries.
    Returns the resolved absolute path.
    """
    bases = allowed_bases or _ALLOWED_BASES
    resolved = path.resolve()
    
    for base in bases:
        try:
            resolved.relative_to(base)
            return resolved
        except ValueError:
            continue
    
    raise ValueError(
        f"Path escapes allowed directories: {path}\n"
        f"Allowed bases: {[str(b) for b in bases]}"
    )


# ── File Size Limits ───────────────────────────────────────────

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def safe_read_file(
    path: Path,
    allowed_bases: Optional[list[Path]] = None,
    max_size: int = MAX_FILE_SIZE,
) -> str:
    """Read a file with atomic open to prevent TOCTOU.
    
    C3 fix: Open file first, then check size after reading.
    No stat() pre-check to eliminate race window.
    """
    safe_path = _validate_path(path, allowed_bases)
    
    # C3 fix: Atomic read - open first, then check size
    try:
        with safe_path.open('r', encoding='utf-8') as f:
            content = f.read()
            # Check size AFTER reading (atomic)
            content_bytes = len(content.encode('utf-8'))
            if content_bytes > max_size:
                raise ValueError(
                    f"文件过大: {content_bytes / 1024 / 1024:.1f}MB，"
                    f"最大允许: {max_size / 1024 / 1024:.1f}MB"
                )
            return content
    except UnicodeDecodeError:
        raise ValueError("文件编码不是UTF-8")


# ── Workspace ──────────────────────────────────────────────────

def ensure_workspace() -> tuple[list[str], list[str]]:
    """Create directory structure. Returns (dirs_created, dirs_skipped)."""
    from . import config
    created: list[str] = []
    skipped: list[str] = []
    for d in config.ALL_DIRS:
        p = config.ROOT_DIR / d
        if p.exists():
            skipped.append(d)
        else:
            p.mkdir(parents=True, exist_ok=True)
            created.append(d)
    return created, skipped


def workspace_initialized() -> bool:
    """Check if workspace has been initialized."""
    from . import config
    return config.DATA_DIR.exists() and config.TEMPLATES_DIR.exists()


def ensure_templates(force: bool = False) -> list[str]:
    """Create default template files. Returns list of created file paths."""
    from . import template_content
    created = []
    for name, content in template_content.TEMPLATES.items():
        p = TEMPLATES_DIR / name
        if p.exists() and not force:
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        created.append(str(p))
    return created


FRONT_MATTER_SEP = "---"


def write_markdown(path: Path, frontmatter: dict, body: str, validate: bool = False, category: Optional[str] = None) -> None:
    """Write a Markdown file with YAML front matter.
    
    Validates path stays within allowed directories before writing.
    If validate=True and category is provided, validates front matter against schema.
    """
    safe_path = _validate_path(path)
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Optional schema validation
    if validate and category:
        from .validation import validate_front_matter
        is_valid, errors = validate_front_matter(frontmatter, category)
        if not is_valid:
            raise ValueError(f"Front matter validation failed: {errors}")
    
    fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = f"---\n{fm_str}---\n\n{body}\n"
    safe_path.write_text(content, encoding="utf-8")


def read_markdown(path: Path) -> tuple[dict, str]:
    """Read a Markdown file with YAML front matter. Returns (frontmatter, body).
    
    Validates path stays within allowed directories before reading.
    """
    safe_path = _validate_path(path)
    text = safe_path.read_text(encoding="utf-8")
    return extract_frontmatter(text)


def extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML front matter and body from markdown text."""
    if text.startswith(FRONT_MATTER_SEP):
        parts = text.split(FRONT_MATTER_SEP, 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                fm = {}
            body = parts[2].strip()
            return fm, body
    return {}, text.strip()


def list_markdown_files(directory: Path) -> list[Path]:
    """Recursively list all .md files in a directory."""
    if not directory.exists():
        return []
    return sorted(directory.rglob("*.md"))


def find_by_id(base_dir: Path, object_id: str) -> Optional[Path]:
    """Find a Markdown file whose front matter 'id' matches object_id."""
    for md_file in list_markdown_files(base_dir):
        try:
            fm, _ = read_markdown(md_file)
            if fm.get("id") == object_id:
                return md_file
        except Exception:
            continue
    return None


def slugify(text: str) -> str:
    """Convert text to a safe filename. Handles Chinese characters gracefully."""
    text = text.strip()
    # Try to keep Chinese characters and alphanumerics
    slug = re.sub(r'[^\w\u4e00-\u9fff\u3400-\u4dbf\-]', '-', text)
    slug = re.sub(r'-+', '-', slug).strip('-')
    if not slug:
        slug = datetime.now().strftime("file-%Y%m%d-%H%M%S")
    # Limit length
    if len(slug) > 80:
        slug = slug[:80]
    return slug


def timestamp_id(prefix: str) -> str:
    """Generate an ID like 'material-20260617-153000-a1b2' with millisecond+random to avoid collisions."""
    import secrets
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:20]  # includes microseconds
    rand = secrets.token_hex(2)
    return f"{prefix}-{ts}-{rand}"


def skill_path_by_status(status: str, skill_id: str) -> Path:
    """Get the file path for a skill with given status."""
    from .config import SKILL_STATUS_DIR, SKILLS_DIR
    subdir = SKILL_STATUS_DIR.get(status, status)
    return SKILLS_DIR / subdir / f"{skill_id}.md"


def all_skill_files() -> list[Path]:
    """List all skill files across all status directories."""
    from .config import SKILLS_DIR
    all_files = []
    for status_dir in SKILLS_DIR.iterdir():
        if status_dir.is_dir():
            all_files.extend(status_dir.rglob("*.md"))
    return sorted(all_files)

