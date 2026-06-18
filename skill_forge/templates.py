from __future__ import annotations
import re
from pathlib import Path
from typing import Any

from .config import TEMPLATES_DIR


def render_template(template_name: str, variables: dict[str, Any]) -> str:
    """Read a template and replace {{key}} placeholders with values.
    
    H4 fix: Escapes template syntax in variable values to prevent injection.
    Path fix: Validates template_name to prevent path traversal.
    """
    # Validate template_name to prevent path traversal
    safe_name = _validate_template_name(template_name)
    template_path = TEMPLATES_DIR / safe_name
    
    if not template_path.exists():
        return f"[模板不存在: {template_name}]"

    text = template_path.read_text(encoding="utf-8")
    
    for key, value in variables.items():
        # H4 fix: Escape template syntax in variable values
        # Coerce non-string values to string so metrics/numbers work safely
        str_value = "" if value is None else str(value)
        safe_value = _escape_template_syntax(str_value)
        text = text.replace("{{" + key + "}}", safe_value)

    # Remove remaining unreplaced placeholders
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    return text


def _validate_template_name(name: str) -> str:
    """Validate template name to prevent path traversal.
    
    Raises ValueError if name contains path separators or escapes TEMPLATES_DIR.
    """
    # Reject path separators
    if '/' in name or '\\' in name or '..' in name:
        raise ValueError(f"Invalid template name: {name}")
    
    # Reject if name starts with dot (hidden files)
    if name.startswith('.'):
        raise ValueError(f"Invalid template name: {name}")
    
    # Resolve and check it stays within TEMPLATES_DIR
    resolved = (TEMPLATES_DIR / name).resolve()
    templates_dir = TEMPLATES_DIR.resolve()
    
    try:
        resolved.relative_to(templates_dir)
    except ValueError:
        raise ValueError(f"Template name escapes templates directory: {name}")
    
    return name


def _escape_template_syntax(text: str) -> str:
    """Escape template syntax characters to prevent injection.
    
    Converts:
    - { → &#123; (HTML entity)
    - } → &#125; (HTML entity)
    
    This prevents attackers from injecting {{config.xxx}} or similar patterns.
    """
    # Escape curly braces using HTML entities
    text = text.replace('{', '&#123;')
    text = text.replace('}', '&#125;')
    return text
