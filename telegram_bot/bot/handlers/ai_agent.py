from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
import asyncio
import time
import logging
import random
from typing import Optional, Set
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.config import settings
# from bot.utils.ai_client import ask_ai, stream_ask_ai
from bot.utils.ai_memory_client import AIMemoryClient
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text
from bot.utils.rag_client import rag_client

from bot.states.registration import (
    QuizSection, StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, MenuSection, RegisteredSection,
)
from bot.handlers.profile import ProfileEditFSM

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# KONSTANTALAR
# ═══════════════════════════════════════════════════════════

MAX_TEXT_LENGTH = 4000
STREAM_EDIT_INTERVAL = 1.0
STREAM_BUFFER_MAX = 1000

# ✨ TEZLIK SOZLAMALARI (yangilangan)
THINKING_FRAME_INTERVAL = 0.12   # ⚡ 0.5 dan 0.12 ga tushirildi — 4x tezroq
TYPING_REFRESH_INTERVAL = 4.0    # typing indicator har 4 sekundda yangilanadi
TYPEWRITER_MIN_DELAY = 0.005     # ⚡ 0.01 dan 0.005 ga (2x tezroq)
TYPEWRITER_MAX_DELAY = 0.015     # ⚡ 0.03 dan 0.015 ga (2x tezroq)
TYPEWRITER_MIN_CHUNK = 8         # ⚡ 5 dan 8 ga (kattaroq chunklar)
TYPEWRITER_MAX_CHUNK = 16        # ⚡ 10 dan 16 ga
TYPEWRITER_EDIT_INTERVAL = 0.03  # ⚡ 0.05 dan 0.03 ga (ko'proq edit qilish)

THINKING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DOTS_FRAMES = [".", "..", "..."]

# ═══════════════════════════════════════════════════════════
# 🔒 DEDUPLICATION — bir xil xabar uchun ikki marta javob bermaslik
# ═══════════════════════════════════════════════════════════

_recently_handled: Set[int] = set()
_RECENTLY_HANDLED_MAX = 500


def _mark_handled(message_id: int) -> bool:
    """
    Xabar ID'ni ro'yxatga qo'shadi.
    Agar allaqachon ishlangan bo'lsa — False qaytaradi (duplicate).
    """
    if message_id in _recently_handled:
        return False
    
    _recently_handled.add(message_id)
    
    # Xotirani tozalash
    if len(_recently_handled) > _RECENTLY_HANDLED_MAX:
        # Eng eski 200 tasini olib tashlash (set tartibsiz, shuning uchun pop)
        for _ in range(200):
            try:
                _recently_handled.pop()
            except KeyError:
                break
    
    return True


# ═══════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════

async def _typing_refresh_task(message: Message, stop_event: asyncio.Event):
    """Background task to keep typing indicator alive until stop_event is set."""
    try:
        while not stop_event.is_set():
            try:
                await message.bot.send_chat_action(message.chat.id, "typing")
            except Exception:
                break
            await asyncio.sleep(TYPING_REFRESH_INTERVAL)
    except asyncio.CancelledError:
        pass

async def _safe_edit_text(
    sent: Message,
    text: str,
    parse_mode: Optional[str] = None,
    retry_count: int = 1
) -> bool:
    """
    Safely edit message text with retry logic.
    Returns True if successful, False otherwise.
    """
    for attempt in range(retry_count + 1):
        try:
            await sent.edit_text(text, parse_mode=parse_mode)
            return True
        
        except TelegramBadRequest as e:
            # "message is not modified" — bu NORMAL, chunki matn bir xil
            if "message is not modified" in str(e).lower():
                return True
            
            # HTML tag yarim ochiq — keyingi edit tuzatadi
            logger.debug(f"[AI] TelegramBadRequest (will retry): {e}")
            if attempt < retry_count:
                await asyncio.sleep(0.1)
                continue
            return True  # Typewriter allaqachon ko'rsatgan
        
        except TelegramRetryAfter as e:
            logger.warning(f"[AI] Rate limit, waiting {e.retry_after}s...")
            await asyncio.sleep(e.retry_after)
            if attempt < retry_count:
                continue
            return False
        
        except TelegramNetworkError as e:
            logger.error(f"[AI] Network error (attempt {attempt + 1}): {e}")
            if attempt < retry_count:
                await asyncio.sleep(1)
                continue
            return False
        
        except Exception as e:
            logger.error(f"[AI] Unexpected error (attempt {attempt + 1}): {e}")
            if attempt < retry_count:
                await asyncio.sleep(1)
                continue
            return False
    
    return False


async def _thinking_animation_task(sent: Message, stop_event: asyncio.Event, base_text: str):

    i = 0
    last_edit_time = 0.0
    
    try:
        while not stop_event.is_set():
            spinner = THINKING_FRAMES[i % len(THINKING_FRAMES)]
            dots = DOTS_FRAMES[(i // 3) % len(DOTS_FRAMES)]  # dots sekinroq o'zgaradi
            frame_text = f"{spinner} {base_text}{dots}"
            
            try:
                await sent.edit_text(frame_text)
            except TelegramBadRequest as e:
                logger.debug(f"TelegramBadRequest in thinking task: {e}")
                break  # ← Task to'xtashi kerak
            except Exception as e:
                logger.error(f"Exception in thinking task: {e}")
                break
            
            i += 1
            # ⚡ TEZROQ: 0.12 soniya (oldingi 0.5 dan 4x tezroq)
            await asyncio.sleep(THINKING_FRAME_INTERVAL)
            
    except asyncio.CancelledError:
        pass


# ═══════════════════════════════════════════════════════════
# AI JAVOB FUNKSIYASI
# ═══════════════════════════════════════════════════════════

async def _answer_with_memory(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Send thinking placeholder (spinner+dots animation), query AI, then typewriter-effect edit."""
    think_text = "Thinking"
    sent = await message.answer(f"{THINKING_FRAMES[0]}{think_text}{DOTS_FRAMES[0]}")

    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(_typing_refresh_task(message, stop_typing))  # ⚠️ `message` bo'lishi kerak, `sent` emas

    stop_thinking = asyncio.Event()
    thinking_task = asyncio.create_task(_thinking_animation_task(sent, stop_thinking, think_text))

    # 🔒 Javob yuborilganligini kuzatish (duplicate javob oldini olish uchun)
    response_sent = False

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

        # Animatsiyani to'xtatamiz
        stop_thinking.set()
        try:
            await thinking_task
        except asyncio.CancelledError:
            pass

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

        # ═══ TYPEWRITER EFFECT (tezlashtirilgan) ═══
        current_text = ""
        last_edit = 0.0
        i = 0
        full_len = len(full_response)

        while i < full_len:
            # ⚡ KATTAROQ CHUNK: 8-16 belgi (oldingi 5-10)
            chunk_length = random.randint(TYPEWRITER_MIN_CHUNK, TYPEWRITER_MAX_CHUNK)
            current_text += full_response[i : i + chunk_length]
            i += chunk_length

            if len(current_text) > MAX_TEXT_LENGTH:
                current_text = current_text[:MAX_TEXT_LENGTH]
                break  # To'xtatamiz, keyin qolganini alohida yuboramiz

            now = time.monotonic()
            # ⚡ KO'PROQ EDIT: 0.03 sekund (oldingi 0.05)
            if now - last_edit >= TYPEWRITER_EDIT_INTERVAL:
                await _safe_edit_text(sent, current_text, parse_mode="HTML", retry_count=1)
                last_edit = now

            # ⚡ TEZROQ: 0.005-0.015 (oldingi 0.01-0.03)
            await asyncio.sleep(random.uniform(TYPEWRITER_MIN_DELAY, TYPEWRITER_MAX_DELAY))

                    # Yakuniy edit — faqat bir marta
            # ═══ YAKUNIY MATNNI KO'RSATISH ═══
        # Typewriter effect allaqachon matnni ko'rsatdi.
        # Endi faqat oxirgi edit qilamiz. Agar ishlamasa — YANGI XABAR YUBORMAYMIZ.

        if len(full_response) > MAX_TEXT_LENGTH:
            # Birinchi qismni edit qilish
            edit_success = await _safe_edit_text(
                sent, 
                full_response[:MAX_TEXT_LENGTH], 
                parse_mode="HTML",
                retry_count=2
            )
            
            # Agar edit ishlamasa, typewriter allaqachon ko'rsatgan — yangi xabar yubormaymiz
            if not edit_success:
                logger.warning(f"[AI] Final edit failed, but typewriter already showed content")
            
            # Qolgan qismlarni yangi xabarlar sifatida yuborish (bu NORMAL)
            remaining = full_response[MAX_TEXT_LENGTH:]
            chunks = [remaining[i:i + MAX_TEXT_LENGTH] for i in range(0, len(remaining), MAX_TEXT_LENGTH)]
            for chunk in chunks:
                await message.answer(chunk, parse_mode="HTML")
                await asyncio.sleep(0.3)
        else:
            # Oddiy holat — faqat edit qilamiz
            edit_success = await _safe_edit_text(
                sent, 
                full_response, 
                parse_mode="HTML",
                retry_count=2
            )
            
            # Agar edit ishlamasa, typewriter allaqachon ko'rsatgan
            if not edit_success:
                logger.warning(f"[AI] Final edit failed, but typewriter already showed content")
            
            response_sent = True

        return response_text

    except Exception as e:
        logger.exception("[AI AGENT MEMORY ERROR]")
        
        # Xato xabarini ko'rsatish
        error_text = get_text("ai.error", lang)
        edit_success = await _safe_edit_text(sent, error_text, retry_count=1)
        
        # Agar edit ishlamasa va typewriter ham hech narsa ko'rsatmagan bo'lsa
        if not edit_success:
            # Faqat shu holatda yangi xabar yuboramiz
            try:
                await message.answer(error_text)
            except Exception:
                pass
        
        return ""   
    
    finally:
        stop_thinking.set()
        stop_typing.set()
        for t in (thinking_task, typing_task):
            try:
                await t
            except asyncio.CancelledError:
                pass


# ═══════════════════════════════════════════════════════════
# HANDLER
# ═══════════════════════════════════════════════════════════

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
    
    # 🔒 DEDUPLICATION: bir xil xabar uchun ikki marta javob bermaslik
    if not _mark_handled(message.message_id):
        logger.warning(f"[AI_HANDLER] Duplicate message skipped: id={message.message_id}")
        return
    
    user_data = await state.get_data()

    logger.info(f"[AI_HANDLER] start: user={message.from_user.id} msg_id={message.message_id}")

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

        # 2. RAG orqali context olish
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