"""Prompt adapter - wraps prompt text for skill melting."""


def to_text(parsed_asset: dict) -> str:
    """Wrap prompt content for LLM consumption."""
    content = parsed_asset.get("content", "")
    title = parsed_asset.get("title", "未命名 Prompt")

    lines = [
        f"## 这是一个外部 Prompt：{title}",
        "",
        "### 可能角色",
        "（由 LLM 分析判断）",
        "",
        "### 可能任务",
        "（由 LLM 分析判断）",
        "",
        "### 原始内容",
        "",
        content,
    ]
    return "\n".join(lines)
