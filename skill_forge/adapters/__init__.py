from .markdown import to_text as md_to_text
from .prompt_adapter import to_text as prompt_to_text
from .generic_agent import to_text as agent_to_text


ADAPTER_MAP = {
    "markdown": md_to_text,
    "agent": agent_to_text,
    "skill": md_to_text,
    "prompt": prompt_to_text,
}


def get_adapter(asset_type: str):
    """Return the to_text function for a given asset type."""
    return ADAPTER_MAP.get(asset_type, md_to_text)


def to_text(parsed_asset: dict) -> str:
    """Convert a parsed asset to unified text for LLM consumption."""
    adapter_fn = get_adapter(parsed_asset.get("type", "markdown"))
    return adapter_fn(parsed_asset)
