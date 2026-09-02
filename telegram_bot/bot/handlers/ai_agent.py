from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
import asyncio
import time
import logging
import random  # ✨ YANGI: Tabiiy typing effekti uchun qo'shildi
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

# ✨ YANGI: RAG Client import
from bot.utils.rag_client import rag_client

from bot.states.registration import (
    QuizSection, StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, MenuSection, RegisteredSection,
)
from bot.handlers.profile import ProfileEditFSM

router = Router()
logger = logging.getLogger(__name__)

MAX_TEXT_LENGTH = 4000
STREAM_EDIT_INTERVAL = 1.0
STREAM_BUFFER_MAX = 1000


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


async def _safe_edit_text(
    sent: Message,
    text: str,
    parse_mode: Optional[str] = None,
    retry_count: int = 1
) -> bool:
    """
    Safely edit message text with retry logic and error handling.
    Returns True if successful, False otherwise.
    """
    for attempt in range(retry_count + 1):
        try:
            await sent.edit_text(text, parse_mode=parse_mode)
            return True
        
        except TelegramBadRequest:
            # HTML tag yarim ochiq bo'lib qolsa, Telegram xato beradi. 
            # Keyingi harfda tag yopiladi, shuning uchun bu xatoni e'tiborsiz qoldiramiz.
            return True
        
        except TelegramRetryAfter as e:
            logger.warning(f"Rate limit hit, waiting {e.retry_after} seconds...")
            await asyncio.sleep(e.retry_after)
            if attempt < retry_count:
                continue
            return False
        
        except TelegramNetworkError as e:
            logger.error(f"Network error on attempt {attempt + 1}: {e}")
            if attempt < retry_count:
                await asyncio.sleep(1)
                continue
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < retry_count:
                await asyncio.sleep(1)
                continue
            return False
    
    return False


async def _answer_with_memory(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Send thinking placeholder, query AI with memory system, and edit message with REALISTIC streaming effect (5-10 chars)."""
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

        header = "🤖 <b>Myestro AI</b>\n\n"
        footer = f"\n\n<i>Model: {model_used} | Time: {time_ms}ms</i>"
        full_response = header + response_text + footer

        # ✨ HAQIQIY TYPING EFFEKTI (5-10 ta harf)
        current_text = ""
        last_edit = 0.0
        i = 0
        full_len = len(full_response)
        
        while i < full_len:
            # 5 dan 10 gacha tasodifiy belgi olish (tabiiy yozish ritmini beradi)
            chunk_length = random.randint(5, 10)
            current_text += full_response[i : i + chunk_length]
            i += chunk_length
            
            if len(current_text) > MAX_TEXT_LENGTH:
                current_text = current_text[:MAX_TEXT_LENGTH]
            
            # Telegram API limitiga tushmaslik uchun kamida 0.05 soniya kutish
            now = time.monotonic()
            if now - last_edit >= 0.05:
                await _safe_edit_text(sent, current_text, parse_mode="HTML", retry_count=1)
                last_edit = now
            
            # Har bir qadamda 0.01 dan 0.03 soniyagacha tasodifiy kutish (inson/AI ritmi)
            await asyncio.sleep(random.uniform(0.01, 0.03))

        # Yakuniy to'liq matnni yuborish (agar xabar juda uzun bo'lsa, bo'laklarga bo'lamiz)
        if len(full_response) > MAX_TEXT_LENGTH:
            try:
                await sent.edit_text(full_response[:MAX_TEXT_LENGTH], parse_mode="HTML")
            except Exception:
                await message.answer(full_response[:MAX_TEXT_LENGTH], parse_mode="HTML")
            
            remaining = full_response[MAX_TEXT_LENGTH:]
            chunks = [remaining[i:i + MAX_TEXT_LENGTH] for i in range(0, len(remaining), MAX_TEXT_LENGTH)]
            for chunk in chunks:
                await message.answer(chunk, parse_mode="HTML")
                await asyncio.sleep(0.5)
        else:
            try:
                await sent.edit_text(full_response, parse_mode="HTML")
            except Exception:
                await message.answer(full_response, parse_mode="HTML")

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


from bot.middlewares.ai_guard import NAVIGATION_WHITELIST

@router.message(
    F.text,
    F.chat.type == "private",
    ~(F.text.in_(NAVIGATION_WHITELIST)),
    ~StateFilter(
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
    """Handle text messages for registered users — AI Teacher with Memory + RAG."""
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
        # 1. Asosiy system promptni olish
        system_prompt = build_system_prompt(lang, cefr_level)

        # ✨ 2. YANGI: RAG orqali context olish va promptga qo'shish
        rag_context = await rag_client.build_context(user_message)
        if rag_context:
            system_prompt += f"\n\n📚 BILIMLAR BAZASI (RAG):\n{rag_context}\n\n⚠️ QOIDA: Yuqoridagi BILIMLAR BAZASI ma'lumotlaridan foydalanib javob bering. Agar savol bu ma'lumotlarga tegishli bo'lmasa, o'z umumiy bilimingizdan foydalaning."

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