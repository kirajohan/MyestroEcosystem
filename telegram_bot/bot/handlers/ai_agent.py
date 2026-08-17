"""AI Agent handler — process text messages via OpenRouter with Memory.

This handler is for REGISTERED users only.
Unregistered users are handled by text.py (fallback AI teacher).
"""

import asyncio
import io
import time
import logging
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.config import settings
from bot.utils.ai_client import ask_ai, stream_ask_ai
from bot.utils.ai_memory_client import AIMemoryClient
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text
from bot.states.registration import (
    QuizSection ,    StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, MenuSection, RegisteredSection,
)
from bot.handlers.profile import ProfileEditFSM
QuizSection

router = Router()
logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 4000  # Telegram message limit

# Stream edit throttle — Telegram rate limit 1 soniyada 1 edit
STREAM_EDIT_INTERVAL = 1.0  # seconds between edits
STREAM_BUFFER_MAX = 1000  # max chars to send per edit


async def _typing_refresh_task(message: Message, stop_event: asyncio.Event):
    """Background task to keep typing indicator alive until stop_event is set."""
    try:
        while not stop_event.is_set():
            try:
                await message.bot.send_chat_action(message.chat.id, "typing")
            except Exception:
                break
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass


async def _stream_answer(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Send thinking placeholder, stream AI chunks, and edit the message."""
    think_text = get_text("ai.thinking", lang)
    sent = await message.answer(think_text)

    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(_typing_refresh_task(sent, stop_typing))

    try:
        last_edit = 0.0
        buffer = ""
        full_text = ""
        async for chunk in stream_ask_ai(
            prompt=user_prompt,
            system_prompt=system_prompt,
        ):
            full_text += chunk
            buffer += chunk
            now = time.monotonic()
            if (now - last_edit >= STREAM_EDIT_INTERVAL) or len(buffer) >= STREAM_BUFFER_MAX:
                preview = think_text if not buffer else buffer
                if len(preview) > MAX_TEXT_LENGTH:
                    preview = preview[: MAX_TEXT_LENGTH - 3] + "..."
                try:
                    await sent.edit_text(preview)
                except Exception:
                    pass
                last_edit = now
                buffer = ""

        final_text = full_text if full_text else get_text("ai.error", lang)
        if len(final_text) > MAX_TEXT_LENGTH:
            final_text = final_text[: MAX_TEXT_LENGTH - 3] + "..."
        try:
            await sent.edit_text(final_text)
        except Exception:
            await message.answer(final_text)
        return full_text
    finally:
        stop_typing.set()
        try:
            await typing_task
        except asyncio.CancelledError:
            pass


async def _answer_with_memory(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Send thinking placeholder, query AI with memory system, and edit message with formatted HTML response."""
    think_text = get_text("ai.thinking", lang)
    sent = await message.answer(think_text)

    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(_typing_refresh_task(sent, stop_typing))

    try:
        ai_memory_client = AIMemoryClient(
            backend_url=settings.BACKEND_URL,
            http_client=None
        )

        response_data = await ai_memory_client.query_with_memory(
            user_id=message.from_user.id,
            message=user_prompt,
            system_prompt=system_prompt,
            model=None
        )

        if isinstance(response_data, dict):
            response_text = response_data.get("response", get_text("ai.error", lang))
            model_used = response_data.get("model_used", "unknown")
            time_ms = response_data.get("processing_time_ms", 0)
        else:
            response_text = getattr(response_data, "response", get_text("ai.error", lang))
            model_used = getattr(response_data, "model_used", "unknown")
            time_ms = getattr(response_data, "processing_time_ms", 0)

        # Header va Footer HTML formatida
        header = "🤖 <b>Myestro AI</b>\n\n"
        footer = f"\n\n<i>Model: {model_used} | Time: {time_ms}ms</i>"
        full_response = header + response_text + footer

        if len(full_response) > MAX_TEXT_LENGTH:
            await sent.edit_text(full_response[:MAX_TEXT_LENGTH], parse_mode="HTML")
            remaining = full_response[MAX_TEXT_LENGTH:]
            chunks = [remaining[i:i + MAX_TEXT_LENGTH] for i in range(0, len(remaining), MAX_TEXT_LENGTH)]
            for chunk in chunks:
                await message.answer(chunk, parse_mode="HTML")
                await asyncio.sleep(0.5)
        else:
            await sent.edit_text(full_response, parse_mode="HTML")

        return response_text

    except Exception as e:
        logger.exception("[AI AGENT MEMORY ERROR]")
        try:
            await sent.edit_text(get_text("ai.error", lang))
        except Exception:
            await message.answer(get_text("ai.error", lang))
        return ""
    finally:
        stop_typing.set()
        try:
            await typing_task
        except asyncio.CancelledError:
            pass


@router.message(
    F.text,
    F.chat.type == "private",
    ~StateFilter(
        # Exclude states where AI should NOT respond
        StartSection.language_selection,
        StartSection.main_menu,
        RegistrationFSM.waiting_name,
        RegistrationFSM.waiting_level,
        AuthFSM.requesting_contact,
        AuthFSM.waiting_password,
        AuthFSM.waiting_name,
        AuthFSM.waiting_email,
        AuthFSM.waiting_password_new,
        AuthFSM.waiting_confirm_password,
        AuthFSM.confirmation,
        RegisterFSM.waiting_name,
        RegisterFSM.waiting_email,
        RegisterFSM.waiting_password,
        RegisterFSM.waiting_confirm_password,
        RegisterFSM.confirmation,
        LoginFSM.waiting_contact_or_email,
        LoginFSM.waiting_password,
        MenuSection.contact_admin,
        ProfileEditFSM.waiting_field,
        ProfileEditFSM.waiting_value,
        QuizSection.cefr_selection,
        QuizSection.quiz_list,
        QuizSection.quiz_active,
        QuizSection.quiz_results,
    ),
    F.text & ~F.text.startswith("/")
)
async def ai_agent_text_handler(message: Message, state: FSMContext):
    """Handle text messages for registered users — AI Teacher with Memory."""
    user_data = await state.get_data()

    print(f"[AI_HANDLER] start: user={message.from_user.id} text='{(message.text or '')[:80]}'")
    logger.info(f"[AI_HANDLER] start: user={message.from_user.id}")

    lang = user_data.get("lang", "uz")
    cefr_level = user_data.get("cefr_level", "A1")
    user_message = message.text.strip()

    if not user_message or len(user_message) > MAX_TEXT_LENGTH:
        logger.debug("[AI_HANDLER] Empty or too long message")
        await message.answer(get_text("ai.error", lang))
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        system_prompt = build_system_prompt(lang, cefr_level)

        logger.debug("[AI_HANDLER] Calling _answer_with_memory()")
        await _answer_with_memory(
            message=message,
            lang=lang,
            system_prompt=system_prompt,
            user_prompt=user_message,
        )
    except Exception as e:
        logger.exception("[AI AGENT ERROR]")
        await message.answer(get_text("ai.error", lang))