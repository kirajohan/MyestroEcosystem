"""AI Agent handler — process text messages via OpenRouter.

This handler is for REGISTERED users only.
Unregistered users are handled by text.py (fallback AI teacher).
"""

import asyncio
import time
from typing import Optional
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.utils.ai_client import stream_ask_ai
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text
from bot.utils.markdown_v2 import sanitize_stream_chunk, extract_media_urls
from bot.states.registration import (
    StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, MenuSection,
    RegisteredSection, LessonsStates, TestStates, InboxState,
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


def _safe_mdv2_text(text: str) -> str:
    """Balance MarkdownV2 markers so Telegram can parse the preview."""
    return sanitize_stream_chunk(text)


async def _send_media(message: Message, media_urls: list):
    """Send photos/videos extracted from AI response."""
    for url in media_urls:
        try:
            low = url.lower()
            if any(ext in low for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
                await message.answer_photo(photo=url)
            else:
                await message.answer_video(video=url)
        except Exception as e:
            logger.warning(f"Media send failed for {url}: {e}")


async def _stream_answer(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Send thinking placeholder, stream AI chunks, and edit the message."""
    # Show thinking placeholder
    think_text = get_text("ai.thinking", lang)
    sent = await message.answer(
        think_text,
        parse_mode=ParseMode.HTML,
    )

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
                preview = _safe_mdv2_text(full_text) if full_text else think_text
                if len(preview) > MAX_TEXT_LENGTH:
                    preview = preview[: MAX_TEXT_LENGTH - 3] + "..."
                try:
                    await sent.edit_text(
                        preview,
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )
                except Exception:
                    # Rate limit or unparseable chunk — try HTML fallback
                    try:
                        await sent.edit_text(preview)
                    except Exception:
                        pass
                last_edit = now
                buffer = ""

        # Final edit with full text (MarkdownV2)
        final_text = full_text if full_text else get_text("ai.error", lang)
        if len(final_text) > MAX_TEXT_LENGTH:
            final_text = final_text[: MAX_TEXT_LENGTH - 3] + "..."
        try:
            await sent.edit_text(
                final_text,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except Exception:
            # fallback: resend as new message if editing failed
            try:
                await message.answer(
                    final_text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            except Exception:
                await message.answer(final_text)

        # Media after the text reply
        await _send_media(message, extract_media_urls(full_text)[1])

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
        None,  # state.clear() dan keyin None state'ga tushib qolishining oldini olish
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
        MenuSection.about_us,
        MenuSection.language_selection,
        MenuSection.settings,
        ProfileEditFSM.waiting_field,
        ProfileEditFSM.waiting_value,
        # Lessons flow — AI aralashmasligi kerak
        LessonsStates.selecting_type,
        LessonsStates.viewing_lessons,
        # Test flow — AI aralashmasligi kerak
        TestStates.selecting_level,
        TestStates.answering_questions,
        TestStates.viewing_results,
        # Inbox flow — AI aralashmasligi kerak
        InboxState.waiting_for_subject,
        InboxState.waiting_for_message,
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
