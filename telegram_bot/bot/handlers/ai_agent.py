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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.config import settings
from bot.utils.ai_memory_client import AIMemoryClient
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text
from bot.utils.rag_client import rag_client

# ✅ YANGI: AI Agent va Tools Service import
from app.models.user import User
from app.services.admin_ai_service import AIToolsService
from app.services.ai_agent import AIAgent

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
THINKING_FRAME_INTERVAL = 0.12
TYPING_REFRESH_INTERVAL = 4.0
TYPEWRITER_MIN_DELAY = 0.005
TYPEWRITER_MAX_DELAY = 0.015
TYPEWRITER_MIN_CHUNK = 8
TYPEWRITER_MAX_CHUNK = 16
TYPEWRITER_EDIT_INTERVAL = 0.03

THINKING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
DOTS_FRAMES = [".", "..", "..."]

# ═══════════════════════════════════════════════════════════
# 🔒 DEDUPLICATION
# ═══════════════════════════════════════════════════════════

_recently_handled: Set[int] = set()
_RECENTLY_HANDLED_MAX = 500

# ═══════════════════════════════════════════════════════════
# MEMORY — Suhbat tarixini saqlash (Redis)
# ═══════════════════════════════════════════════════════════

import json
from redis.asyncio import Redis

MEMORY_KEY_PREFIX = "ai_chat_history:"
MEMORY_MAX_MESSAGES = 20  # Oxirgi 20 ta xabarni saqlash
MEMORY_TTL = 3600 * 24    # 24 soat

import re

def sanitize_to_telegram_html(text: str) -> str:
    """
    Markdown belgilarini Telegram HTML ga aylantiradi.
    AI noto'g'ri format yuborgan taqdirda ham xavfsiz qiladi.
    """
    if not text:
        return text
    
    # 1. Kod bloklarni olib tashlash (```...```)
    text = re.sub(r'```(?:\w+)?\n?', '', text)
    
    # 2. ### Sarlavhalar → <b> + ajratuvchi
    def convert_heading(match):
        level = len(match.group(1))  # nechta # borligi
        heading_text = match.group(2).strip()
        if level == 1:
            return f"\n\n📌 <b>{heading_text.upper()}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        elif level == 2:
            return f"\n\n🔹 <b>{heading_text}</b>\n"
        else:
            return f"\n\n▫️ <b>{heading_text}</b>\n"
    
    text = re.sub(r'^(#{1,6})\s+(.+)$', convert_heading, text, flags=re.MULTILINE)
    
    # 3. **qalin** → <b>qalin</b>
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # 4. *kursiv* → <i>kursiv</i> (ehtiyot bo'ling: ro'yxat * bilan aralashmasligi uchun)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    
    # 5. `kod` → <code>kod</code>
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    # 6. Ro'yxatlar: "- " va "* " → "• "
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)
    
    # 7. Raqamli ro'yxatlarni saqlab qolish (1. 2. 3.)
    # (o'zgartirmaymiz)
    
    # 8. Yopilmagan teglarni tekshirish (xavfsizlik)
    text = _fix_unclosed_tags(text)
    
    return text


def _fix_unclosed_tags(text: str) -> str:
    """Yopilmagan HTML teglarni tuzatish."""
    tags_to_check = ['b', 'i', 'u', 's', 'code', 'blockquote', 'a']
    
    for tag in tags_to_check:
        # Ochilgan teglar soni
        open_count = len(re.findall(f'<{tag}[^>]*>', text))
        # Yopilgan teglar soni
        close_count = len(re.findall(f'</{tag}>', text))
        
        # Agar ochilgan ko'p bo'lsa, yopilmaganlarni qo'shish
        diff = open_count - close_count
        if diff > 0:
            text += f'</{tag}>' * diff
        # Agar yopilgan ko'p bo'lsa, ortiqcha yopilganlarni olib tashlash
        elif diff < 0:
            for _ in range(abs(diff)):
                text = re.sub(f'</{tag}>', '', text, count=1)
    
    return text


async def _get_chat_history(redis: Redis, user_id: int) -> list[dict]:
    """Foydalanuvchining suhbat tarixini Redis'dan olish."""
    try:
        key = f"{MEMORY_KEY_PREFIX}{user_id}"
        raw = await redis.get(key)
        if raw:
            history = json.loads(raw)
            return history[-MEMORY_MAX_MESSAGES:]  # Oxirgi N ta xabar
    except Exception as e:
        logger.warning(f"[Memory] Tarixni olish xatosi: {e}")
    return []


async def _save_chat_message(redis: Redis, user_id: int, role: str, content: str):
    """Yangi xabarni suhbat tarixiga qo'shish."""
    try:
        key = f"{MEMORY_KEY_PREFIX}{user_id}"
        raw = await redis.get(key)
        history = json.loads(raw) if raw else []
        
        history.append({"role": role, "content": content})
        
        # Faqat oxirgi N ta xabarni saqlash
        history = history[-MEMORY_MAX_MESSAGES:]
        
        await redis.set(key, json.dumps(history, ensure_ascii=False), ex=MEMORY_TTL)
    except Exception as e:
        logger.warning(f"[Memory] Xabarni saqlash xatosi: {e}")

def _mark_handled(message_id: int) -> bool:
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


# ═══════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════

async def _typing_refresh_task(message: Message, stop_event: asyncio.Event):
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
    for attempt in range(retry_count + 1):
        try:
            await sent.edit_text(text, parse_mode=parse_mode)
            return True
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                return True
            logger.debug(f"[AI] TelegramBadRequest (will retry): {e}")
            if attempt < retry_count:
                await asyncio.sleep(0.1)
                continue
            return True
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
    try:
        while not stop_event.is_set():
            spinner = THINKING_FRAMES[i % len(THINKING_FRAMES)]
            dots = DOTS_FRAMES[(i // 3) % len(DOTS_FRAMES)]
            frame_text = f"{spinner} {base_text}{dots}"
            try:
                await sent.edit_text(frame_text)
            except TelegramBadRequest as e:
                logger.debug(f"TelegramBadRequest in thinking task: {e}")
                break
            except Exception as e:
                logger.error(f"Exception in thinking task: {e}")
                break
            i += 1
            await asyncio.sleep(THINKING_FRAME_INTERVAL)
    except asyncio.CancelledError:
        pass


# ═══════════════════════════════════════════════════════════
# TYPEWRITER — umumiy funksiya (ikki rejim uchun)
# ═══════════════════════════════════════════════════════════

async def _typewriter_send(
    sent: Message,
    message: Message,
    full_response: str,
    lang: str,
) -> str:
    """Typewriter effect bilan xabarni yuborish."""
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
        edit_success = await _safe_edit_text(
            sent, full_response[:MAX_TEXT_LENGTH], parse_mode="HTML", retry_count=2
        )
        if not edit_success:
            logger.warning("[AI] Final edit failed, but typewriter already showed content")
        remaining = full_response[MAX_TEXT_LENGTH:]
        chunks = [remaining[i:i + MAX_TEXT_LENGTH] for i in range(0, len(remaining), MAX_TEXT_LENGTH)]
        for chunk in chunks:
            await message.answer(chunk, parse_mode="HTML")
            await asyncio.sleep(0.3)
    else:
        edit_success = await _safe_edit_text(sent, full_response, parse_mode="HTML", retry_count=2)
        if not edit_success:
            logger.warning("[AI] Final edit failed, but typewriter already showed content")

    return full_response


# ═══════════════════════════════════════════════════════════
# REJIM 1: AI TEACHER (Memory + RAG) — Eski logika
# ═══════════════════════════════════════════════════════════

async def _answer_with_memory(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Oddiy AI Teacher rejimi (Memory + RAG)."""
    think_text = "Thinking"
    sent = await message.answer(f"{THINKING_FRAMES[0]}{think_text}{DOTS_FRAMES[0]}")

    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(_typing_refresh_task(message, stop_typing))

    stop_thinking = asyncio.Event()
    thinking_task = asyncio.create_task(_thinking_animation_task(sent, stop_thinking, think_text))

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

        await _typewriter_send(sent, message, full_response, lang)
        return response_text

    except Exception as e:
        logger.exception("[AI AGENT MEMORY ERROR]")
        error_text = get_text("ai.error", lang)
        edit_success = await _safe_edit_text(sent, error_text, retry_count=1)
        if not edit_success:
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
# REJIM 2: UNIFIED AI AGENT (Tool Calling + AI Teacher)
# ═══════════════════════════════════════════════════════════

async def _answer_with_agent(
    message: Message,
    session: AsyncSession,
    db_user: User,
    lang: str,
    cefr_level: str,
    user_prompt: str,
    redis: Redis,  # ✅ YANGI: Redis dependency
) -> str:
    """
    Unified AI Agent — Tool Calling + Oddiy suhbat + MEMORY.
    Admin va User uchun bitta handler.
    """
    is_admin = (db_user.role == "admin")
    
    # Thinking placeholder
    think_text = "O'ylayapman" if lang == "uz" else "Thinking"
    sent = await message.answer(f"{THINKING_FRAMES[0]}{think_text}{DOTS_FRAMES[0]}")

    stop_typing = asyncio.Event()
    typing_task = asyncio.create_task(_typing_refresh_task(message, stop_typing))

    stop_thinking = asyncio.Event()
    thinking_task = asyncio.create_task(_thinking_animation_task(sent, stop_thinking, think_text))

    try:
        # ✅ 1. Suhbat tarixini Redis'dan olish
        history = await _get_chat_history(redis, db_user.telegram_id)
        logger.debug(f"[Memory] User {db_user.telegram_id}: {len(history)} xabar tarixdan")

        # 2. Tools service yaratish
        tools_service = AIToolsService(
            db=session,
            current_user_id=db_user.id,
            is_admin=is_admin,
        )

        # 3. AI Agent yaratish
        agent = AIAgent(tools_service, is_admin=is_admin)

        # 4. Qo'shimcha kontekst (RAG + AI Teacher prompt)
        additional_context_parts = [
            f"Foydalanuvchi tili: {lang}",
            f"Foydalanuvchi CEFR darajasi: {cefr_level}",
            f"Role: {'Admin' if is_admin else 'Oddiy foydalanuvchi'}",
            f"Foydalanuvchi ismi: {db_user.full_name or db_user.telegram_username or 'Noma\'lum'}",
        ]

        # RAG (faqat user uchun)
        if not is_admin:
            try:
                rag_context = await rag_client.build_context(user_prompt)
                if rag_context:
                    additional_context_parts.append(
                        f"📚 BILIMLAR BAZASI (RAG):\n{rag_context}\n\n"
                        f"⚠️ Agar savol bu ma'lumotlarga tegishli bo'lsa, ulardan foydalan."
                    )
            except Exception as e:
                logger.warning(f"RAG xatosi: {e}")

        additional_context = "\n".join(additional_context_parts)

        # 5. AI Agent'dan javob olish (TARIX BILAN!)
        answer = await agent.chat(
            user_message=user_prompt,
            history=history,  # ✅ Suhbat tarixi
            additional_context=additional_context,
        )

        # 6. Animatsiyani to'xtatish
        stop_thinking.set()
        try:
            await thinking_task
        except asyncio.CancelledError:
            pass

        # ✅ 7. Suhbat tarixini yangilash (user xabari + AI javobi)
        await _save_chat_message(redis, db_user.telegram_id, "user", user_prompt)
        await _save_chat_message(redis, db_user.telegram_id, "assistant", answer)

        # 8. Javobni formatlash
        header = "👑 <b>Admin AI</b>\n\n" if is_admin else "🤖 <b>Myestro AI</b>\n\n"
        answer = sanitize_to_telegram_html(answer)
        full_response = header + answer
        # 9. Typewriter bilan yuborish
        await _typewriter_send(sent, message, full_response, lang)
        return answer

    except Exception as e:
        logger.exception("[Unified AI Agent Error]")
        stop_thinking.set()
        try:
            await thinking_task
        except:
            pass
        
        error_text = get_text("ai.error", lang)
        edit_success = await _safe_edit_text(sent, error_text, retry_count=1)
        if not edit_success:
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
# MAIN HANDLER — Unified (AI Agent + Fallback AI Teacher)
# ═══════════════════════════════════════════════════════════
from bot.states.reminder_states import ReminderFSM
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
        ReminderFSM.waiting_text,
        ReminderFSM.waiting_type,
        ReminderFSM.waiting_time,
        ReminderFSM.waiting_day,
        ReminderFSM.waiting_datetime,
        ReminderFSM.confirm,
    ),
    F.text & ~F.text.startswith("/")
)
async def ai_agent_text_handler(
    message: Message, 
    state: FSMContext,
    session: AsyncSession,  # ✅ DB session dependency injection
):
    """
    🎯 Unified AI Handler:
    - Admin uchun: 40+ tool (butun DB) + oddiy suhbat
    - User uchun: 5 tool (o'z ma'lumotlari) + AI Teacher + RAG
    - Fallback: Eski AIMemoryClient (agar DB session yo'q bo'lsa)
    """
    
    # 🔒 DEDUPLICATION
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
        # 1. DB'dan user'ni olish
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            # ✅ Redis client yaratish
            from redis.asyncio import Redis as AsyncRedis
            from bot.config import settings as bot_settings
            
            redis_client = AsyncRedis.from_url(
                bot_settings.REDIS_URL,
                decode_responses=True
            )
            
            try:
                logger.info(f"[AI_HANDLER] Unified AI Agent (role={db_user.role})")
                await _answer_with_agent(
                    message=message,
                    session=session,
                    db_user=db_user,
                    lang=lang,
                    cefr_level=cefr_level,
                    user_prompt=user_message,
                    redis=redis_client,
                )
            finally:
                await redis_client.close()
                
        else:
            # ⚠️ FALLBACK: Eski AI Teacher
            logger.warning("[AI_HANDLER] User not in DB, fallback to AI Teacher")
            system_prompt = build_system_prompt(lang, cefr_level)

            rag_context = await rag_client.build_context(user_message)
            if rag_context:
                system_prompt += (
                    f"\n\n📚 BILIMLAR BAZASI (RAG):\n{rag_context}\n\n"
                    f"⚠️ QOIDA: Yuqoridagi ma'lumotlardan foydalanib javob bering."
                )

            await _answer_with_memory(
                message=message,
                lang=lang,
                system_prompt=system_prompt,
                user_prompt=user_message,
            )

    except Exception as e:
        logger.exception("[AI AGENT ERROR]")
        await message.answer(get_text("ai.error", lang))
