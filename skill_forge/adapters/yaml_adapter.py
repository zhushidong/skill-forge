"""YAML adapter - formats YAML and highlights capability fields."""

import yaml


CAPABILITY_KEYS = {"instructions", "tools", "prompts", "skills", "workflows", "agents", "name", "description"}


def to_text(parsed_asset: dict) -> str:
    """Return formatted YAML text with capability highlights."""
    content = parsed_asset.get("content", "")
    metadata = parsed_asset.get("metadata", {})
    lines = []

    # Try to parse and re-dump the YAML
    try:
        data = yaml.safe_load(content)
        formatted = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        lines.append(formatted)
    except yaml.YAMLError:
        lines.append(content)

    # Highlight capability fields
    keys = metadata.get("top_level_keys", [])
    capability_keys_found = set(keys) & CAPABILITY_KEYS
    if capability_keys_found:
        lines.append("")
        lines.append("---")
        lines.append(f"可能的能力字段：{', '.join(sorted(capability_keys_found))}")

    return "\n".join(lines)
