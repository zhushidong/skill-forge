"""Generic agent adapter - wraps agent/skill/workflow documents for melting."""

import json
import yaml

from .constants import CAPABILITY_KEYS


STRUCTURED_FIELDS = [
    "name", "agent_name", "skill_name", "description", "goal", "objectives",
    "instructions", "system_prompt", "role", "tools", "skills", "workflows",
    "agents", "constraints", "memory", "steps", "rules",
]


def _extract_fields(content: str) -> dict:
    """Try to extract structured fields from JSON/YAML/markdown content."""
    # Try JSON first
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, TypeError):
        pass

    # Try YAML
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            return data
    except yaml.YAMLError:
        pass

    return {}


def _get_field(data: dict, *keys) -> any:
    """Get first matching field from data."""
    for key in keys:
        if key in data:
            return data[key]
    return None


def to_text(parsed_asset: dict) -> str:
    """Wrap agent/skill/workflow document for LLM consumption with field extraction."""
    content = parsed_asset.get("content", "")
    title = parsed_asset.get("title", "未命名 Agent")
    file_type = parsed_asset.get("type", "unknown")

    data = _extract_fields(content)

    lines = [f"# 外部资产：{title}", f"文件类型：{file_type}", ""]

    # Extract structured fields
    extracted = {}
    for field in STRUCTURED_FIELDS:
        if field in data:
            extracted[field] = data[field]

    if extracted:
        lines.append("## 提取到的结构化字段")
        for key, value in extracted.items():
            marker = " [能力字段]" if key in CAPABILITY_KEYS else ""
            if isinstance(value, str):
                preview = value[:200] + "..." if len(value) > 200 else value
                lines.append(f"- {key}{marker}: {preview}")
            elif isinstance(value, list):
                lines.append(f"- {key}{marker}: [列表，共{len(value)}项]")
                for item in value[:5]:
                    item_str = str(item)[:80]
                    lines.append(f"  - {item_str}")
            elif isinstance(value, dict):
                lines.append(f"- {key}{marker}: {{字典}}")
                for k, v in value.items():
                    v_str = str(v)[:80]
                    lines.append(f"  - {k}: {v_str}")
            else:
                lines.append(f"- {key}{marker}: {value}")
        lines.append("")

    # List possible capabilities
    capability_keys_found = set(data.keys()) & CAPABILITY_KEYS
    if capability_keys_found:
        lines.append("## 可能包含的能力")
        for key in sorted(capability_keys_found):
            lines.append(f"- {key}")
        lines.append("")

    lines.append("## 原始内容")
    lines.append("")
    lines.append(content)
    return "\n".join(lines)
