from __future__ import annotations
from pathlib import Path
import json

import yaml

from .storage import _validate_path, MAX_FILE_SIZE


# ── Parser ─────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}


def parse_external_file(path: Path, asset_type: str = "auto") -> dict:
    """Parse an external file and return a standardized dict.
    
    Validates path and uses atomic read to prevent TOCTOU.
    
    Returns:
        {
            "type": "...",
            "title": "...",
            "content": "...",
            "metadata": {...}
        }
    """
    # C1 fix: Validate path before reading
    safe_path = _validate_path(path)
    
    # C3 fix: Atomic read - open first, then check size
    try:
        with safe_path.open('r', encoding='utf-8') as f:
            text = f.read()
            # Check size AFTER reading (atomic)
            content_bytes = len(text.encode('utf-8'))
            if content_bytes > MAX_FILE_SIZE:
                raise ValueError(
                    f"文件过大: {content_bytes / 1024 / 1024:.1f}MB，"
                    f"最大允许: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                )
    except UnicodeDecodeError:
        raise ValueError("文件编码不是UTF-8")

    suffix = safe_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"当前 MVP 只支持 md/txt/json/yaml/yml，请先将 {safe_path.name} 转成文本。"
        )

    metadata: dict = {}
    content = text
    title = safe_path.stem

    if suffix == ".json":
        try:
            data = json.loads(text)
            content = json.dumps(data, indent=2, ensure_ascii=False)
            if isinstance(data, dict):
                metadata["top_level_keys"] = list(data.keys())
                if "name" in data:
                    title = data["name"]
                if "title" in data:
                    title = data["title"]
        except json.JSONDecodeError:
            pass

    elif suffix in (".yaml", ".yml"):
        try:
            data = yaml.safe_load(text)
            content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
            if isinstance(data, dict):
                metadata["top_level_keys"] = list(data.keys())
                if "name" in data:
                    title = data["name"]
                if "title" in data:
                    title = data["title"]
        except yaml.YAMLError:
            pass

    # Determine asset type from extension/content
    if asset_type == "auto":
        asset_type = _guess_type(suffix, text, metadata)

    return {
        "type": asset_type,
        "title": title,
        "content": text,
        "metadata": metadata,
    }


def _guess_type(suffix: str, text: str, metadata: dict) -> str:
    """Guess asset type from extension and content."""
    keys = metadata.get("top_level_keys", [])
    if suffix in (".json", ".yaml", ".yml"):
        if any(k in keys for k in ("agent", "instructions", "tools", "workflows")):
            return "agent"
        if any(k in keys for k in ("skills", "skill")):
            return "skill"
        if any(k in keys for k in ("prompts", "prompt", "instructions")):
            return "prompt"
    return "markdown"
