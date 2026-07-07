import re
from typing import Optional


def clean_telegram_text(text: str) -> str:
    """Remove HTML tags and trim whitespace."""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text to Telegram's message limit."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
