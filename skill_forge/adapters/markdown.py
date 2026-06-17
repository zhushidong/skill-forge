"""Markdown adapter - returns the raw content."""


def to_text(parsed_asset: dict) -> str:
    """Return the raw markdown content."""
    return parsed_asset.get("content", "")
