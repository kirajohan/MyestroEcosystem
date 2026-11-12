"""Har user uchun bir vaqtda faqat bitta AI so'rov (lock) + Stop tugma."""

import asyncio
import logging
from typing import Awaitable, Dict, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

AI_STOP_CALLBACK = "ai_stop"
# Qattiq tashqi limit. StreamRenderer o'zining yumshoq limiti (SOFT_LIMIT) bilan undan oldin
# foydalanuvchiga xabar berib yakunlaydi; bu — oxirgi himoya.
AI_TIMEOUT_SECONDS = 300

_active_tasks: Dict[int, asyncio.Task] = {}
_stopped: set = set()


def stop_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="⏹ Stop", callback_data=AI_STOP_CALLBACK)]]
    )


def is_busy(user_id: int) -> bool:
    task = _active_tasks.get(user_id)
    return task is not None and not task.done()


async def run_exclusive(user_id: int, coro: Awaitable) -> bool:
    """
    coro'ni user uchun yagona faol task sifatida ishga tushiradi.
    Qaytaradi: True — tugadi, False — to'xtatildi (Stop) yoki vaqt tugadi.
    Band bo'lsa coro yopiladi va RuntimeError ko'tariladi (oldin is_busy tekshiring).
    """
    if is_busy(user_id):
        coro.close()
        raise RuntimeError("AI task already running")

    task = asyncio.create_task(asyncio.wait_for(coro, AI_TIMEOUT_SECONDS))
    _active_tasks[user_id] = task
    task.add_done_callback(
        lambda t: _active_tasks.pop(user_id, None) if _active_tasks.get(user_id) is t else None
    )
    try:
        await task
        return True
    except asyncio.CancelledError:
        if user_id in _stopped:
            return False  # Stop tugma bosildi
        raise  # handlerning o'zi bekor qilingan (masalan, shutdown)
    except asyncio.TimeoutError:
        logger.warning(f"[AI-LOCK] timeout user={user_id}")
        return False
    finally:
        # Stop va normal tugash poygasida qolib ketmasligi uchun doim tozalanadi
        _stopped.discard(user_id)


def cancel(user_id: int) -> bool:
    task: Optional[asyncio.Task] = _active_tasks.get(user_id)
    if task and not task.done():
        _stopped.add(user_id)
        task.cancel()
        return True
    return False
