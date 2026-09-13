"""
AI Agent utility funksiyalari.
Typewriter effect, thinking animation, safe edit va boshqalar.
"""
import asyncio
import random
import time
import logging
from typing import Optional, Set

from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramNetworkError

from bot.config import settings
from bot.utils.ai_memory_client import AIMemoryClient
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 4000
THINKING_FRAME_INTERVAL = 0.12
TYPING_REFRESH_INTERVAL = 4.0
TYPEWRITER_MIN_DELAY = 0.005
TYPEWRITER_MAX_DELAY = 0.015
TYPEWRITER_MIN_CHUNK = 8
TYPEWRITER_MAX_CHUNK = 16
TYPEWRITER_EDIT_INTERVAL = 0.03

THINKING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DOTS_FRAMES = [".", "..", "..."]

_recently_handled: Set[int] = set()
_RECENTLY_HANDLED_MAX = 500


def _mark_handled(message_id: int) -> bool:
    """Deduplication — bir xil xabar uchun ikki marta javob bermaslik."""
    if message_id in _recently_handled:
        return False
    _recently_handled.add(message_id)
    if len(_recently_handled) > _RECENTLY_HANDLED_MAX:
        for _ in range(200):
            try:
                _recently_handled.pop()
            except KeyError:
                break
    return True


async def _safe_edit_text(
    sent: Message,
    text: str,
    parse_mode: Optional[str] = None,
    retry_count: int = 1,
) -> bool:
    """Xavfsiz xabar tahrirlash."""
    for attempt in range(retry_count + 1):
        try:
            await sent.edit_text(text, parse_mode=parse_mode)
            return True
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                return True
            if attempt < retry_count:
                await asyncio.sleep(0.1)
                continue
            return True
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            if attempt < retry_count:
                continue
            return False
        except Exception as e:
            logger.error(f"Edit error: {e}")
            if attempt < retry_count:
                await asyncio.sleep(1)
                continue
            return False
    return False


async def _answer_with_typewriter(
    sent: Message,
    original_message: Message,
    full_response: str,
):
    """Typewriter effect bilan xabar yuborish."""
    current_text = ""
    last_edit = 0.0
    i = 0
    full_len = len(full_response)

    while i < full_len:
        chunk_length = random.randint(TYPEWRITER_MIN_CHUNK, TYPEWRITER_MAX_CHUNK)
        current_text += full_response[i : i + chunk_length]
        i += chunk_length

        if len(current_text) > MAX_TEXT_LENGTH:
            current_text = current_text[:MAX_TEXT_LENGTH]
            break

        now = time.monotonic()
        if now - last_edit >= TYPEWRITER_EDIT_INTERVAL:
            await _safe_edit_text(sent, current_text, parse_mode="HTML", retry_count=1)
            last_edit = now

        await asyncio.sleep(random.uniform(TYPEWRITER_MIN_DELAY, TYPEWRITER_MAX_DELAY))

    # Yakuniy edit
    if len(full_response) > MAX_TEXT_LENGTH:
        await _safe_edit_text(
            sent, full_response[:MAX_TEXT_LENGTH], parse_mode="HTML", retry_count=2
        )
        remaining = full_response[MAX_TEXT_LENGTH:]
        chunks = [remaining[i : i + MAX_TEXT_LENGTH] for i in range(0, len(remaining), MAX_TEXT_LENGTH)]
        for chunk in chunks:
            await original_message.answer(chunk, parse_mode="HTML")
            await asyncio.sleep(0.3)
    else:
        await _safe_edit_text(sent, full_response, parse_mode="HTML", retry_count=2)


# Eski funksiya (fallback uchun)
async def _answer_with_memory(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Oddiy AI Teacher rejimi (AIMemoryClient bilan)."""
    think_text = "Thinking"
    sent = await message.answer(f"{THINKING_FRAMES[0]}{think_text}{DOTS_FRAMES[0]}")

    try:
        ai_memory_client = AIMemoryClient(
            backend_url=settings.BACKEND_URL,
            http_client=None,
        )

        response_data = await ai_memory_client.query_with_memory(
            user_id=message.from_user.id,
            message=user_prompt,
            system_prompt=system_prompt,
            model=None,
        )

        if isinstance(response_data, dict):
            response_text = response_data.get("response", get_text("ai.error", lang))
            model_used = response_data.get("model_used", "unknown")
            time_ms = response_data.get("processing_time_ms", 0)
        else:
            response_text = getattr(response_data, "response", get_text("ai.error", lang))
            model_used = getattr(response_data, "model_used", "unknown")
            time_ms = getattr(response_data, "processing_time_ms", 0)

        header = "🤖 <b>Myestro AI</b>\n\n"
        footer = f"\n\n<i>Model: {model_used} | Time: {time_ms}ms</i>"
        full_response = header + response_text + footer

        await _answer_with_typewriter(sent, message, full_response)
        return response_text

    except Exception as e:
        logger.exception("[AI MEMORY ERROR]")
        await _safe_edit_text(sent, get_text("ai.error", lang), retry_count=1)
        return ""