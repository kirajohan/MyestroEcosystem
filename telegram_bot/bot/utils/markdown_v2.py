"""MarkdownV2 utilities for Telegram messages.

Telegram MarkdownV2 special characters that must be escaped:
    _ * [ ] ( ) ~ ` > # + - = | { } . !

Provides:
- escape_markdown_v2()       — escape raw text
- md_*()                     — inline formatting helpers
- sanitize_stream_chunk()    — safe partial streaming text
- extract_media_urls()       — detect media tags in AI response
"""

import re
from typing import Optional, List, Tuple

MARKDOWN_V2_SPECIAL = r"_*[]()~`>#+-=|{}.!"


def escape_markdown_v2(text: str) -> str:
    """Escape ALL MarkdownV2 special characters."""
    if not text:
        return ""
    return "".join(f"\\{ch}" if ch in MARKDOWN_V2_SPECIAL else ch for ch in text)


def md_bold(text: str) -> str:
    return f"*{text}*"


def md_italic(text: str) -> str:
    return f"_{text}_"


def md_underline(text: str) -> str:
    return f"__{text}__"


def md_strike(text: str) -> str:
    return f"~{text}~"


def md_code(text: str) -> str:
    return f"`{text}`"


def md_pre(text: str, language: Optional[str] = None) -> str:
    if language:
        return f"```{language}\n{text}\n```"
    return f"```\n{text}\n```"


def md_link(text: str, url: str) -> str:
    safe_text = escape_markdown_v2(text)
    safe_url = url.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"[{safe_text}]({safe_url})"


def md_quote(text: str) -> str:
    lines = text.splitlines() or [""]
    return "\n".join(f"> {line}" for line in lines)


def md_header(level: int, text: str) -> str:
    return md_bold(text)


def md_table(headers: list, rows: list) -> str:
    if not headers or not rows:
        return ""
    header_line = "| " + " | ".join(escape_markdown_v2(str(h)) for h in headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = []
    for row in rows[:20]:
        body_lines.append("| " + " | ".join(escape_markdown_v2(str(c)) for c in row) + " |")
    return "\n".join([header_line, separator] + body_lines)


def _count_unclosed_marker(text: str, marker: str) -> int:
    """Count OPEN (unclosed) markers of a given type, skipping escaped chars."""
    count = 0
    i = 0
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i : i + len(marker)] == marker:
            count += 1
            i += len(marker)
        else:
            i += 1
    return count


def sanitize_stream_chunk(text: str) -> str:
    """Make partial streaming text safe for MarkdownV2.

    Closes any unclosed inline marker so Telegram can parse the preview.
    """
    if not text:
        return ""
    for marker in ("```", "**", "__", "~~", "`", "*", "_", "~"):
        if _count_unclosed_marker(text, marker) % 2 == 1:
            text += marker
    return text


def extract_media_urls(text: str) -> Tuple[str, List[str]]:
    """Extract media URLs from AI response.

    Formats: [media: <URL>] or ![alt](URL)
    Returns (cleaned_text, media_urls).
    """
    if not text:
        return "", []
    media_urls = []
    media_pattern = re.compile(r"\[media:\s*(https?://[^\s\]]+)\s*\]", re.IGNORECASE)
    media_urls.extend(m.group(1) for m in media_pattern.finditer(text))
    cleaned = media_pattern.sub("", text)
    img_pattern = re.compile(r"!\[([^\]]*)\]\((https?://[^\s)\]]+)\)")
    media_urls.extend(m.group(2) for m in img_pattern.finditer(cleaned))
    cleaned = img_pattern.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned, list(media_urls)
