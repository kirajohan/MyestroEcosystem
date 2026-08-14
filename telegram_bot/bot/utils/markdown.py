"""HTML escaping utilities for Telegram bot messages.

Since all bot messages are sent with parse_mode="HTML", we need to escape
HTML special characters that could break parsing.
"""

_AMP = chr(38) + "amp;"
_LT = chr(38) + "lt;"
_GT = chr(38) + "gt;"
_QUOT = chr(38) + "quot;"
_APOS = chr(38) + "#39;"


def escape_html(text: object) -> str:
    """Escape HTML special characters in the given text.

    Telegram HTML parse mode requires escaping of: & < > " '
    This function converts any input (str, int, float, etc.) to a string and
    escapes all reserved characters so the text can be safely sent with
    parse_mode="HTML".

    Args:
        text: Any value to escape (will be converted to str).

    Returns:
        str: The escaped text safe for HTML parsing.
    """
    if text is None:
        return ""
    s = str(text)
    # Replace & first to avoid double escaping
    s = s.replace(chr(38), _AMP)
    s = s.replace(chr(60), _LT)
    s = s.replace(chr(62), _GT)
    s = s.replace(chr(34), _QUOT)
    s = s.replace(chr(39), _APOS)
    return s


# Backward compatibility alias
escape_md = escape_html