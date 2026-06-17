"""Generic agent adapter - wraps agent documents for skill melting."""


def to_text(parsed_asset: dict) -> str:
    """Wrap agent document for LLM consumption."""
    content = parsed_asset.get("content", "")
    title = parsed_asset.get("title", "未命名 Agent")

    lines = [
        f"## 外部 Agent：{title}",
        "",
        "### 可能包含",
        "- 目标",
        "- 指令 (instructions)",
        "- 工具 (tools)",
        "- 工作流 (workflows)",
        "- 约束",
        "- 记忆",
        "- 可转化 Skill",
        "",
        "### 原始内容",
        "",
        content,
    ]
    return "\n".join(lines)
