"""AI Agent handler — process text and voice messages via OpenRouter.

This handler is for REGISTERED users only.
Unregistered users are handled by text.py (fallback AI teacher).
"""

import asyncio
import io
import time
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.config import settings
from bot.utils.ai_client import ask_ai, stream_ask_ai, transcribe_voice, transcribe_voice_via_service
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text
from bot.states.registration import (
    StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, MenuSection, RegisteredSection
)
from bot.handlers.profile import ProfileEditFSM

import logging
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
    # Show thinking placeholder
    think_text = get_text("ai.thinking", lang)
    sent = await message.answer(think_text)

    # Background typing refresh
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
                # Truncate on Telegram 4096 char safety
                if len(preview) > MAX_TEXT_LENGTH:
                    preview = preview[: MAX_TEXT_LENGTH - 3] + "..."
                try:
                    await sent.edit_text(preview)
                except Exception:
                    # Ignore rate limit or unchanged content errors during streaming
                    pass
                last_edit = now
                buffer = ""

        # Final edit with full text
        final_text = full_text if full_text else get_text("ai.error", lang)
        if len(final_text) > MAX_TEXT_LENGTH:
            final_text = final_text[: MAX_TEXT_LENGTH - 3] + "..."
        try:
            await sent.edit_text(final_text)
        except Exception:
            # fallback: send as new message if editing failed
            await message.answer(final_text)
        return full_text
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
        RegistrationFSM.phone_request,
        RegistrationFSM.phone_verified,
        RegistrationFSM.waiting_name,
        RegistrationFSM.waiting_birthdate,
        RegistrationFSM.waiting_level,
        RegistrationFSM.confirmation,
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
    )
)
async def ai_agent_text_handler(message: Message, state: FSMContext):
    """Handle text messages for registered users — AI Teacher."""
    user_data = await state.get_data()

    # Debug log entry
    print(f"[AI_HANDLER] start: user={message.from_user.id} text='{(message.text or '')[:80]}'")
    logger.info(f"[AI_HANDLER] start: user={message.from_user.id}")

    # Allow both registered and unregistered users — RegistrationMiddleware controls flow
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

        # Prefer streaming for UX; non-streaming fallback via ask_ai is not used here
        # because stream_ask_ai already handles non-stream text via its fallback path.
        logger.debug("[AI_HANDLER] Calling _stream_answer()")
        await _stream_answer(
            message=message,
            lang=lang,
            system_prompt=system_prompt,
            user_prompt=user_message,
        )
    except Exception as e:
        logger.exception("[AI AGENT ERROR]")
        await message.answer(get_text("ai.error", lang))


@router.message(
    F.voice,
    F.chat.type == "private",
    ~StateFilter(
        # Exclude states where AI should NOT respond
        StartSection.language_selection,
        StartSection.main_menu,
        RegistrationFSM.phone_request,
        RegistrationFSM.phone_verified,
        RegistrationFSM.waiting_name,
        RegistrationFSM.waiting_birthdate,
        RegistrationFSM.waiting_level,
        RegistrationFSM.confirmation,
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
    )
)
async def ai_agent_voice_handler(message: Message, state: FSMContext):
    """Handle voice messages — transcribe + AI Teacher."""
    user_data = await state.get_data()
    
    lang = user_data.get("lang", "uz")
    cefr_level = user_data.get("cefr_level", "A1")

    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # 1. Download voice file
        voice_file = await message.bot.get_file(message.voice.file_id)
        voice_bytes = await message.bot.download_file(voice_file.file_path)
        voice_data = voice_bytes.read()

        # 2. Transcribe via Whisper Service (fallback: OpenRouter)
        transcribed = await transcribe_voice_via_service(voice_data)

        if not transcribed:
            transcribed = await transcribe_voice(voice_data)

        if not transcribed:
            await message.answer(get_text("ai.error", lang))
            return

        # 3. Send transcription to AI with streaming UX
        system_prompt = build_system_prompt(lang, cefr_level)
        ai_prompt = f"[Voice message transcribed]: {transcribed}\n\nPlease respond to this message."

        ai_response = await _stream_answer(
            message=message,
            lang=lang,
            system_prompt=system_prompt,
            user_prompt=ai_prompt,
        )

        # 4. Streaming answer already sent; no need to duplicate.
    except Exception as e:
        print(f"[AI AGENT VOICE ERROR] {e}")
        await message.answer(get_text("ai.error", lang))
