"""
AI agent yozish amallari uchun tasdiqlash ombori (PendingAction).

Admin yozish tool'ini (rol o'zgartirish, broadcast, inbox javobi va h.k.) chaqirganda amal
darhol bajarilmaydi: Redis'ga TTL bilan saqlanadi, chatda "Tasdiqlash / Bekor" tugmalari chiqadi.
Faqat so'ragan admin tasdiqlaganda (bir martalik) amal bajariladi.
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from redis.asyncio import Redis

from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)

PENDING_TTL_SECONDS = 300
PENDING_PREFIX = "ai_pending:"
CONFIRM_PREFIX = "ai_ok:"
CANCEL_PREFIX = "ai_no:"

CONFIRM_TITLE = {
    "uz": "⚠️ <b>Tasdiqlash kerak</b>",
    "ru": "⚠️ <b>Требуется подтверждение</b>",
    "en": "⚠️ <b>Confirmation required</b>",
}


class PendingStore:
    """AIToolsService.pending_store interfeysi: `await create(action, params, summary) -> id`."""

    def __init__(self, redis: Redis, owner_telegram_id: int):
        self.redis = redis
        self.owner = owner_telegram_id
        self.created: List[Tuple[str, str]] = []  # (action_id, summary) — chatda tugma ko'rsatish uchun

    async def create(self, action: str, params: Dict[str, Any], summary: str) -> str:
        action_id = uuid.uuid4().hex[:16]
        payload = {"owner": self.owner, "action": action, "params": params, "summary": summary}
        await self.redis.set(f"{PENDING_PREFIX}{action_id}", json.dumps(payload, ensure_ascii=False), ex=PENDING_TTL_SECONDS)
        self.created.append((action_id, summary))
        return action_id


async def peek(redis: Redis, action_id: str) -> Optional[Dict[str, Any]]:
    raw = await redis.get(f"{PENDING_PREFIX}{action_id}")
    return json.loads(raw) if raw else None


async def take(redis: Redis, action_id: str) -> Optional[Dict[str, Any]]:
    """Bir martalik olish (atomik GETDEL): ikkinchi bosish None qaytaradi."""
    raw = await redis.getdel(f"{PENDING_PREFIX}{action_id}")
    return json.loads(raw) if raw else None


def confirm_kb(action_id: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=get_text("ai.confirm", lang), callback_data=f"{CONFIRM_PREFIX}{action_id}"),
        InlineKeyboardButton(text=get_text("ai.cancel", lang), callback_data=f"{CANCEL_PREFIX}{action_id}"),
    ]])
