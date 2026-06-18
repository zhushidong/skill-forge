from __future__ import annotations
from pathlib import Path
import json

import yaml

from .storage import MAX_FILE_SIZE


# ── External File Reader ───────────────────────────────────────

def read_external_file(path: Path, max_size: int = MAX_FILE_SIZE) -> str:
    """Read an arbitrary user-provided file with size protection.

    Unlike safe_read_file, this does not restrict the path to the workspace,
    because CLI commands explicitly ask the user for an external file path.
    """
    if not path.exists():
        raise ValueError(f"文件不存在: {path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {path}")

    try:
        with path.open('r', encoding='utf-8') as f:
            content = f.read()
            content_bytes = len(content.encode('utf-8'))
            if content_bytes > max_size:
                raise ValueError(
                    f"文件过大: {content_bytes / 1024 / 1024:.1f}MB，"
                    f"最大允许: {max_size / 1024 / 1024:.1f}MB"
                )
            return content
    except UnicodeDecodeError:
        raise ValueError("文件编码不是UTF-8")


# ── Parser ─────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}


def parse_external_file(path: Path, asset_type: str = "auto") -> dict:
    """Parse an external file and return a standardized dict.
    
    Validates that the path exists and is a file, uses atomic read to prevent TOCTOU.
    Read paths are not restricted to workspace because users may melt arbitrary files.
    
    Returns:
        {
            "type": "...",
            "title": "...",
            "content": "...",
            "metadata": {...}
        }
    """
    if not path.exists():
        raise ValueError(f"文件不存在: {path}")
    if not path.is_file():
        raise ValueError(f"路径不是文件: {path}")

    # Atomic read - open first, then check size
    try:
        with path.open('r', encoding='utf-8') as f:
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

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"当前 MVP 只支持 md/txt/json/yaml/yml，请先将 {path.name} 转成文本。"
        )

    metadata: dict = {}
    content = text
    title = path.stem

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

    # Determine file type from extension
    file_type = "markdown"
    if suffix == ".json":
        file_type = "json"
    elif suffix in (".yaml", ".yml"):
        file_type = "yaml"
    elif suffix == ".txt":
        file_type = "text"

    # Determine asset type from extension/content (for template context)
    guessed_asset_type = asset_type
    if asset_type == "auto":
        guessed_asset_type = _guess_type(suffix, text, metadata)

    return {
        "type": file_type,
        "asset_type": guessed_asset_type,
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
