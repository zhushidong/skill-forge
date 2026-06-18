from __future__ import annotations
import os
import re
from typing import Optional

from . import config


# ── Input Sanitization (C1/C2: LLM Prompt Injection Prevention) ───

def sanitize_user_input(text: str) -> str:
    """Sanitize user input to prevent prompt injection attacks.
    
    Handles:
    - Common injection phrases
    - Base64/URL/Unicode encoding bypass
    - Zero-width characters and homoglyphs (C1 fix)
    - Length limits
    """
    if not text:
        return text
    
    import unicodedata
    
    # C1 fix: Unicode NFKC normalization to collapse homoglyphs
    # Cyrillic 'а' (U+0430) → Latin 'a' (U+0061)
    text = unicodedata.normalize('NFKC', text)
    
    # C1 fix: Strip zero-width characters
    zero_width_chars = re.compile(r'[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180e\u2000-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u206f\u3000\ufeff]')
    text = zero_width_chars.sub('', text)
    
    # 1. Remove common injection patterns
    injection_patterns = [
        (r'(?i)ignore\s+previous\s+instructions', '[FILTERED]'),
        (r'(?i)you\s+are\s+now', '[FILTERED]'),
        (r'(?i)system\s*:', '[FILTERED]'),
        (r'(?i)assistant\s*:', '[FILTERED]'),
        (r'(?i)new\s+instructions?\s*:', '[FILTERED]'),
        (r'(?i)disregard\s+all', '[FILTERED]'),
        (r'(?i)override\s+safety', '[FILTERED]'),
        (r'(?i)bypass\s+filter', '[FILTERED]'),
        (r'(?i)jailbreak', '[FILTERED]'),
        (r'(?i)DAN\s+mode', '[FILTERED]'),
        (r'---\s*\n', '---\n'),
    ]
    for pattern, replacement in injection_patterns:
        text = re.sub(pattern, replacement, text)
    
    # 2. Filter encoding bypass
    text = re.sub(r'base64\s*[:=]\s*[A-Za-z0-9+/=]{20,}', '[FILTERED]', text, flags=re.IGNORECASE)
    text = re.sub(r'%[0-9A-Fa-f]{2}', '[FILTERED]', text)
    text = re.sub(r'\\u[0-9A-Fa-f]{4}', '[FILTERED]', text)
    text = re.sub(r'\\U[0-9A-Fa-f]{8}', '[FILTERED]', text)
    text = re.sub(r'&#x?[0-9a-fA-F]+;', '[FILTERED]', text)
    
    # 3. Filter role impersonation patterns
    role_patterns = [
        (r'(?i)you\s+are\s+a\s+(?:root|admin|system|developer)', '[FILTERED]'),
        (r'(?i)act\s+as\s+(?:root|admin|system|developer)', '[FILTERED]'),
        (r'(?i)pretend\s+(?:to\s+be|you\s+are)', '[FILTERED]'),
        (r'(?i)roleplay\s+as', '[FILTERED]'),
        (r'(?i)simulate\s+(?:being|a)', '[FILTERED]'),
    ]
    for pattern, replacement in role_patterns:
        text = re.sub(pattern, replacement, text)
    
    # 4. Limit length
    max_input_length = 50000
    if len(text) > max_input_length:
        text = text[:max_input_length] + "\n\n[输入被截断]"
    
    return text


# ── LLM Output Sanitization ────────────────────────────────────

def sanitize_llm_output(text: str) -> str:
    """Remove YAML front matter blocks that LLM might inject.
    
    Attackers can inject:---
    id: malicious
    ---
    which would corrupt read_markdown parsing.
    
    Strategy: strip all --- blocks that look like YAML front matter.
    """
    if not text:
        return text
    
    # Remove leading --- block (YAML front matter injection)
    text = re.sub(
        r'^---\s*\n(.*?\n)---\s*\n',
        '',
        text,
        count=1,
        flags=re.DOTALL
    )
    
    # Remove trailing --- block
    text = re.sub(
        r'\n---\s*\n(.*?)\s*$',
        '',
        text,
        count=1,
        flags=re.DOTALL
    )
    
    return text.strip()


# ── Error Message Sanitization (M3) ────────────────────────────

def sanitize_error_message(error: str) -> str:
    """Sanitize error messages to prevent sensitive information leakage.
    
    Returns user-friendly messages for known errors.
    Never returns the original error to avoid path/key leakage.
    """
    if not error:
        return "未知错误"
    
    error_str = str(error)
    error_lower = error_str.lower()
    
    # Return user-friendly messages (never return filtered original)
    if "api_key" in error_lower or "sk-" in error_lower or "unauthorized" in error_lower or "401" in error_lower:
        return "API Key 无效或未设置"
    elif "rate_limit" in error_lower or "429" in error_lower:
        return "API 调用频率超限，请稍后再试"
    elif "timeout" in error_lower:
        return "API 调用超时，请稍后再试"
    elif "model" in error_lower and ("not" in error_lower or "found" in error_lower):
        return "模型不可用"
    elif "connection" in error_lower or "network" in error_lower:
        return "网络连接失败，请检查网络"
    elif "file" in error_lower and ("not found" in error_lower or "找不到" in error_lower):
        return "文件不存在"
    elif "permission" in error_lower or "access denied" in error_lower:
        return "权限不足"
    else:
        return "操作失败，请检查输入和配置"


# ── LLM Configuration ──────────────────────────────────────────

DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_RETRIES = 2
DEFAULT_MAX_TOKENS = 4096


def _create_client():
    """Create OpenAI client with timeout and optional base URL."""
    from openai import OpenAI
    kwargs = {
        "api_key": config.OPENAI_API_KEY,
        "timeout": DEFAULT_TIMEOUT,
        "max_retries": DEFAULT_MAX_RETRIES,
    }
    if config.OPENAI_BASE_URL:
        kwargs["base_url"] = config.OPENAI_BASE_URL
    return OpenAI(**kwargs)


def has_api_key() -> bool:
    """Check if an API key is configured."""
    return bool(config.OPENAI_API_KEY)


def run_llm(prompt: str, model: Optional[str] = None) -> str:
    """Run LLM or return a fallback prompt for manual use.
    
    If OPENAI_API_KEY is set, call the OpenAI API.
    Otherwise, return a markdown text with the full prompt for the user to copy.
    
    Output is sanitized to prevent front matter injection.
    """
    if not has_api_key():
        return _fallback_prompt(prompt)

    try:
        client = _create_client()
        use_model = model or config.DEFAULT_MODEL
        response = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": "你是一个商业 Skill 炼丹炉助手。请用 Markdown 输出。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        raw_output = response.choices[0].message.content or ""
        return sanitize_llm_output(raw_output)
    except Exception as e:
        return _fallback_prompt(prompt, error=sanitize_error_message(e))


def run_llm_with_history(prompt: str, history: list[dict], model: Optional[str] = None) -> str:
    """Run LLM with conversation history for drill mode.
    
    Output is sanitized to prevent front matter injection.
    """
    if not has_api_key():
        return _fallback_prompt(prompt)

    try:
        client = _create_client()
        use_model = model or config.DEFAULT_MODEL
        messages = [
            {"role": "system", "content": "你是一个商业 Skill 炼丹炉助手。请用 Markdown 输出。"},
            {"role": "user", "content": prompt},
        ] + history
        response = client.chat.completions.create(
            model=use_model,
            messages=messages,
            temperature=0.7,
            max_tokens=DEFAULT_MAX_TOKENS,
        )
        raw_output = response.choices[0].message.content or ""
        return sanitize_llm_output(raw_output)
    except Exception as e:
        return _fallback_prompt(prompt, error=sanitize_error_message(e))


def _fallback_prompt(prompt: str, error: Optional[str] = None) -> str:
    """Generate fallback prompt for manual use when API key is not available."""
    error_line = ""
    if error:
        safe_error = sanitize_error_message(error)
        if safe_error not in ("未知错误", "操作失败，请检查输入和配置"):
            error_line = f"\n> **API 调用失败**: {safe_error}\n"
    return f"""## 未检测到 OPENAI_API_KEY

你可以将以下 Prompt 复制到任意大模型中使用：

- ChatGPT
- Claude
- Kimi
- DeepSeek
- Gemini
- 本地模型
{error_line}

---

{prompt}
"""
