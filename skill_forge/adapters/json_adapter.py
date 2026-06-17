"""JSON adapter - formats JSON and highlights capability fields."""

import json


CAPABILITY_KEYS = {"instructions", "tools", "prompts", "skills", "workflows", "agents", "name", "description"}


def to_text(parsed_asset: dict) -> str:
    """Return formatted JSON text with capability highlights."""
    content = parsed_asset.get("content", "")
    metadata = parsed_asset.get("metadata", {})
    lines = []

    # Try to pretty-print the JSON
    try:
        data = json.loads(content)
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        lines.append(formatted)
    except (json.JSONDecodeError, TypeError):
        lines.append(content)

    # Highlight capability fields
    keys = metadata.get("top_level_keys", [])
    capability_keys_found = set(keys) & CAPABILITY_KEYS
    if capability_keys_found:
        lines.append("")
        lines.append("---")
        lines.append(f"可能的能力字段：{', '.join(sorted(capability_keys_found))}")

    return "\n".join(lines)
