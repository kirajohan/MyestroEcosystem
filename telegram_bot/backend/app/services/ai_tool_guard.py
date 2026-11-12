"""
AI tool argumentlarini tekshirish (LLM yuborgan argumentlarga ishonmaymiz).

Tool schema'siga ko'ra: noma'lum argumentlar tashlanadi, turlar majburlanadi,
sonlar cheklanadi, enum tekshiriladi, matnlar qisqartiriladi.
"""
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Nom bo'yicha son chegaralari (min, max)
_INT_BOUNDS = {
    "limit": (1, 50),
    "offset": (0, 10_000),
    "days": (1, 365),
}
_DEFAULT_INT_BOUNDS = (-2_147_483_648, 2_147_483_647)

# Uzun matn kutiladigan maydonlar
_LONG_TEXT_FIELDS = {"text", "message", "ai_prompt", "title", "content", "reply"}
_SHORT_MAX = 200
_LONG_MAX = 1000

MAX_TOOL_RESULT_CHARS = 12_000


def sanitize_args(schema: Dict[str, Any], args: Any) -> Dict[str, Any]:
    """Tool `parameters` schema'siga mos xavfsiz argumentlar lug'atini qaytaradi."""
    if not isinstance(args, dict):
        return {}

    properties = (schema or {}).get("properties", {}) or {}
    clean: Dict[str, Any] = {}

    for name, spec in properties.items():
        if name not in args or args[name] is None:
            continue
        value = args[name]
        ptype = spec.get("type")

        try:
            if ptype == "integer":
                if isinstance(value, bool):
                    continue
                value = int(value)
                lo, hi = _INT_BOUNDS.get(name, _DEFAULT_INT_BOUNDS)
                value = max(lo, min(hi, value))
            elif ptype == "number":
                if isinstance(value, bool):
                    continue
                value = float(value)
            elif ptype == "boolean":
                if not isinstance(value, bool):
                    continue
            elif ptype == "string":
                value = str(value)
                limit = spec.get("maxLength") or (_LONG_MAX if name in _LONG_TEXT_FIELDS else _SHORT_MAX)
                value = value.replace("\x00", "")[:limit]
            else:
                # array/object — kutilmagan; tashlaymiz
                continue
        except (TypeError, ValueError):
            continue

        enum = spec.get("enum")
        if enum and value not in enum:
            continue

        clean[name] = value

    dropped = set(args) - set(clean)
    if dropped:
        logger.debug(f"[TOOL-GUARD] argumentlar tashlandi: {sorted(dropped)}")
    return clean


def serialize_tool_result(result: Any) -> str:
    """Tool natijasini LLM uchun JSON qiladi: uzunligi cheklangan."""
    text = json.dumps({"data": result}, ensure_ascii=False, default=str)
    if len(text) > MAX_TOOL_RESULT_CHARS:
        text = json.dumps(
            {
                "data": text[:MAX_TOOL_RESULT_CHARS],
                "truncated": True,
                "note": "Natija uzun bo'lgani uchun qisqartirildi; limit/filtrni toraytiring.",
            },
            ensure_ascii=False,
        )
    return text
