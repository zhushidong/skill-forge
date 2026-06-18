"""Adapters package: convert parsed assets to unified text for LLM."""

from .constants import CAPABILITY_KEYS
from .markdown import to_text as markdown_to_text
from .json_adapter import to_text as json_to_text
from .yaml_adapter import to_text as yaml_to_text
from .prompt_adapter import to_text as prompt_to_text
from .generic_agent import to_text as generic_agent_to_text


def to_text(parsed_asset: dict, asset_type: str = "auto") -> str:
    """Convert parsed asset to unified text based on file type and asset type."""
    file_type = parsed_asset.get("type", "text")

    # Explicit asset type routing
    if asset_type in ("prompt",):
        return prompt_to_text(parsed_asset)
    if asset_type in ("agent", "external_agent", "skill", "external_skill", "workflow"):
        return generic_agent_to_text(parsed_asset)

    # File type routing
    if file_type == "json":
        return json_to_text(parsed_asset)
    if file_type in ("yaml", "yml"):
        return yaml_to_text(parsed_asset)
    if file_type == "markdown":
        return markdown_to_text(parsed_asset)

    # Default
    return markdown_to_text(parsed_asset)
