"""YAML adapter - formats YAML and highlights capability fields with value previews."""

import yaml

from .constants import CAPABILITY_KEYS


def _preview_value(value, max_len: int = 100) -> str:
    """Generate a short preview of a value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        text = value.strip()
        if len(text) > max_len:
            return text[:max_len] + "..."
        return text
    if isinstance(value, list):
        if not value:
            return "[空列表]"
        previews = [_preview_value(v, 40) for v in value[:3]]
        suffix = f" 等共{len(value)}项" if len(value) > 3 else ""
        return "[列表: " + ", ".join(previews) + suffix + "]"
    if isinstance(value, dict):
        if not value:
            return "{空字典}"
        keys = list(value.keys())[:5]
        return "{字典: keys=[" + ", ".join(keys) + ("..." if len(value) > 5 else "") + "]}"
    return f"<{type(value).__name__}>"


def to_text(parsed_asset: dict) -> str:
    """Return formatted YAML text with capability highlights and value previews."""
    content = parsed_asset.get("content", "")
    title = parsed_asset.get("title", "未命名 YAML 资产")
    lines = [f"# {title}", ""]

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError:
        lines.append("原始内容：")
        lines.append("```yaml")
        lines.append(content)
        lines.append("```")
        return "\n".join(lines)

    lines.append("顶层字段预览：")
    if isinstance(data, dict):
        for key in data.keys():
            preview = _preview_value(data[key])
            marker = " [能力字段]" if key in CAPABILITY_KEYS else ""
            lines.append(f"- {key}{marker}: {preview}")
    elif isinstance(data, list):
        lines.append(f"- 列表，共 {len(data)} 项")
    else:
        lines.append(f"- {data}")

    lines.append("")
    lines.append("原始内容：")
    lines.append("```yaml")
    lines.append(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))
    lines.append("```")
    return "\n".join(lines)
