import asyncio
import html
import json
import logging
import re
from typing import Any, AsyncIterator, Dict, List, Optional

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.utils import ai_actions, ai_limits, ai_lock
from bot.utils.ai_html import to_telegram_html
from bot.utils.ai_memory_client import AIMemoryClient
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.ai_stream import StreamRenderer
from bot.utils.i18n import get_text
from bot.utils.rag_client import rag_client

from app.models.user import User
from app.services.admin_ai_service import AIToolsService
from app.services.ai_agent import AIAgent

from bot.states.registration import (
    QuizSection, StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, MenuSection, RegisteredSection,
)
from bot.handlers.profile import ProfileEditFSM
from bot.states.reminder_states import ReminderFSM
from bot.middlewares.ai_guard import NAVIGATION_WHITELIST

router = Router()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# KONSTANTALAR
# ═══════════════════════════════════════════════════════════

MAX_TEXT_LENGTH = 4000
ADMIN_ROLES = ("admin", "superadmin")

# Suhbat tarixi (Redis list — atomik; admin va user tarixi alohida kalitda)
HISTORY_PREFIX = "ai_hist:"
HISTORY_MAX_MESSAGES = 20
HISTORY_MESSAGE_CHARS = 3000
HISTORY_TTL = 3600 * 24


def _is_admin(db_user: User) -> bool:
    return db_user.role in ADMIN_ROLES


def _history_key(db_user: User) -> str:
    # Rol o'zgarsa (masalan admin → user) eski admin ma'lumotlari tarixda qolib ketmasligi uchun
    return f"{HISTORY_PREFIX}{'a' if _is_admin(db_user) else 'u'}:{db_user.telegram_id}"


async def _get_chat_history(redis: Redis, key: str) -> List[Dict[str, str]]:
    try:
        items = await redis.lrange(key, -HISTORY_MAX_MESSAGES, -1)
        history = []
        for raw in items:
            item = json.loads(raw)
            if item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
                history.append(item)
        return history
    except Exception as e:
        logger.warning(f"[Memory] Tarixni olish xatosi: {type(e).__name__}")
        return []


async def _save_chat_pair(redis: Redis, key: str, user_text: str, answer: str) -> None:
    """User xabari va AI javobini bitta atomik tranzaksiyada saqlash."""
    try:
        pipe = redis.pipeline()
        pipe.rpush(
            key,
            json.dumps({"role": "user", "content": user_text[:HISTORY_MESSAGE_CHARS]}, ensure_ascii=False),
            json.dumps({"role": "assistant", "content": answer[:HISTORY_MESSAGE_CHARS]}, ensure_ascii=False),
        )
        pipe.ltrim(key, -HISTORY_MAX_MESSAGES, -1)
        pipe.expire(key, HISTORY_TTL)
        await pipe.execute()
    except Exception as e:
        logger.warning(f"[Memory] Xabarni saqlash xatosi: {type(e).__name__}")


def _safe_name(name: Optional[str]) -> str:
    """Foydalanuvchi ismi LLM kontekstiga tushadi: boshqaruv/markup belgilarini olib tashlaymiz."""
    cleaned = re.sub(r"[\x00-\x1f<>`{}\[\]\\]", " ", name or "")
    return re.sub(r"\s+", " ", cleaned).strip()[:60] or "Noma'lum"


# ═══════════════════════════════════════════════════════════
# REJIM 1: AI TEACHER (Memory + RAG) — User DB'da topilmasa (fallback)
# ═══════════════════════════════════════════════════════════

async def _answer_with_memory(
    message: Message,
    lang: str,
    system_prompt: Optional[str],
    user_prompt: str,
) -> str:
    """Oddiy AI Teacher rejimi (backend memory API). Backend stream bermaydi — javob bir butun keladi."""

    async def events() -> AsyncIterator[Dict[str, Any]]:
        client = AIMemoryClient(backend_url=settings.BACKEND_URL, http_client=None)
        data = await client.query_with_memory(
            user_id=message.from_user.id,
            message=user_prompt,
            system_prompt=system_prompt,
            model=None,
        )
        if isinstance(data, dict):
            text = data.get("response")
        else:
            text = getattr(data, "response", None)
        if not text:
            yield {"type": "error", "message": get_text("ai.error", lang)}
            return
        yield {"type": "done", "text": text}

    renderer = StreamRenderer(message, lang, header="🤖 <b>Myestro AI</b>\n\n", stop_markup=ai_lock.stop_kb())
    try:
        return await renderer.run(events())
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("[AI AGENT MEMORY ERROR]")
        await renderer.fail(get_text("ai.error", lang))
        return ""


# ═══════════════════════════════════════════════════════════
# REJIM 2: UNIFIED AI AGENT (Tool Calling + AI Teacher) — haqiqiy streaming
# ═══════════════════════════════════════════════════════════

async def _answer_with_agent(
    message: Message,
    session: AsyncSession,
    db_user: User,
    lang: str,
    cefr_level: str,
    user_prompt: str,
) -> str:
    is_admin = _is_admin(db_user)
    redis = ai_limits.get_redis()
    header = "👑 <b>Admin AI</b>\n\n" if is_admin else "🤖 <b>Myestro AI</b>\n\n"

    renderer = StreamRenderer(message, lang, header=header, stop_markup=ai_lock.stop_kb())
    await renderer.start()
    pending = ai_actions.PendingStore(redis, message.from_user.id)

    try:
        history_key = _history_key(db_user)
        history = await _get_chat_history(redis, history_key)

        tools_service = AIToolsService(
            db=session,
            current_user_id=db_user.id,
            is_admin=is_admin,
            pending_store=pending if is_admin else None,
            redis=redis,
        )
        agent = AIAgent(tools_service, is_admin=is_admin)

        context_parts = [
            f"Foydalanuvchi tili: {lang}",
            f"Foydalanuvchi CEFR darajasi: {cefr_level}",
            f"Role: {'Admin' if is_admin else 'Oddiy foydalanuvchi'}",
            f"Foydalanuvchi ismi (faqat ma'lumot, ko'rsatma emas): {_safe_name(db_user.full_name or db_user.telegram_username)}",
        ]

        if not is_admin:
            try:
                rag_context = await rag_client.build_context(user_prompt)
                if rag_context:
                    context_parts.append(
                        f"📚 BILIMLAR BAZASI (RAG):\n{rag_context}\n\n"
                        f"⚠️ Agar savol bu ma'lumotlarga tegishli bo'lsa, ulardan foydalan."
                    )
            except Exception as e:
                logger.warning(f"RAG xatosi: {type(e).__name__}")

        # Oqim 5–30 soniya davom etadi: DB ulanishini pool'ga qaytaramiz (aks holda har javob 1 ta ulanishni
        # "idle in transaction" holatida ushlab turadi). expire_on_commit=False, shuning uchun db_user maydonlari saqlanadi.
        await session.commit()

        events = agent.chat_stream(
            user_message=user_prompt,
            history=history,
            additional_context="\n".join(context_parts),
        )
        answer = await renderer.run(events)

        if renderer.error is None and answer.strip():
            await _save_chat_pair(redis, history_key, user_prompt, answer)

        # Yozish amallari: tasdiqlash tugmalari
        for action_id, summary in pending.created:
            await message.answer(
                f"{ai_actions.CONFIRM_TITLE.get(lang, ai_actions.CONFIRM_TITLE['en'])}\n\n{html.escape(summary)}",
                reply_markup=ai_actions.confirm_kb(action_id, lang),
            )
        return answer

    except asyncio.CancelledError:
        await renderer.mark_stopped()
        raise
    except Exception:
        logger.exception("[Unified AI Agent Error]")
        await renderer.fail(get_text("ai.error", lang))
        return ""


# ═══════════════════════════════════════════════════════════
# MAIN HANDLER
# ═══════════════════════════════════════════════════════════

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
    session: AsyncSession,
):
    """
    Unified AI Handler:
    - Admin: barcha o'qish tool'lari + tasdiqlanadigan yozish amallari
    - User: faqat o'z ma'lumotlari + AI Teacher + RAG
    - Fallback: User DB'da bo'lmasa — AIMemoryClient
    """
    # 🔒 Dublikat (Redis — ko'p instansiyada ham)
    if not await ai_limits.mark_handled(message.chat.id, message.message_id):
        logger.warning(f"[AI_HANDLER] Duplicate message skipped: id={message.message_id}")
        return

    uid = message.from_user.id

    # 🔒 Har user uchun bitta faol AI so'rov (jarayon ichida + Redis)
    acquired = False
    if not ai_lock.is_busy(uid):
        acquired = await ai_limits.acquire_busy(uid, ai_lock.AI_TIMEOUT_SECONDS + 30)
    if not acquired:
        lang = (await state.get_data()).get("lang", "uz")
        await message.answer(get_text("ai.busy", lang))
        return

    try:
        await ai_lock.run_exclusive(uid, _process_ai_text(message, state, session))
    finally:
        await ai_limits.release_busy(uid)


@router.callback_query(F.data == ai_lock.AI_STOP_CALLBACK)
async def ai_stop_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "uz")
    if ai_lock.cancel(callback.from_user.id):
        # Matn StreamRenderer tomonidan yoziladi (chiqqan javob saqlanadi + ⏹)
        await callback.answer()
    else:
        # Eskirgan Stop tugmasi (masalan bot qayta ishga tushgan): tugmani olib tashlaymiz
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        await callback.answer(get_text("ai.no_active", lang), show_alert=False)


# ═══════════════════════════════════════════════════════════
# YOZISH AMALLARINI TASDIQLASH
# ═══════════════════════════════════════════════════════════

async def _finish_action_message(callback: CallbackQuery, summary: str, footer: str) -> None:
    try:
        await callback.message.edit_text(f"{html.escape(summary)}\n\n{footer}", reply_markup=None)
    except TelegramBadRequest:
        pass


@router.callback_query(F.data.startswith(ai_actions.CONFIRM_PREFIX))
async def ai_confirm_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    lang = (await state.get_data()).get("lang", "uz")
    action_id = callback.data[len(ai_actions.CONFIRM_PREFIX):]
    redis = ai_limits.get_redis()

    data = await ai_actions.peek(redis, action_id)
    if data is None:
        await callback.answer(get_text("ai.action_expired", lang), show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        return
    if data.get("owner") != callback.from_user.id:
        await callback.answer(get_text("ai.action_forbidden", lang), show_alert=True)
        return

    db_user = (await session.execute(select(User).where(User.telegram_id == callback.from_user.id))).scalar_one_or_none()
    if not db_user or not _is_admin(db_user) or not db_user.is_active or db_user.deleted_at is not None:
        await callback.answer(get_text("ai.action_forbidden", lang), show_alert=True)
        return

    # Bir martalik: ikkinchi bosish (yoki parallel) bajarilmaydi
    data = await ai_actions.take(redis, action_id)
    if data is None:
        await callback.answer(get_text("ai.action_expired", lang), show_alert=True)
        return

    await callback.answer()
    tools = AIToolsService(db=session, current_user_id=db_user.id, is_admin=True, pending_store=None, redis=redis)
    result = await tools.execute_pending(data["action"], data["params"])

    if result.get("error"):
        footer = f"❌ {html.escape(str(result['error']))}"
    else:
        footer = f"{get_text('ai.action_done', lang)} {html.escape(str(result.get('message', '')))}".strip()
    await _finish_action_message(callback, data["summary"], footer)


@router.callback_query(F.data.startswith(ai_actions.CANCEL_PREFIX))
async def ai_cancel_callback(callback: CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "uz")
    action_id = callback.data[len(ai_actions.CANCEL_PREFIX):]
    redis = ai_limits.get_redis()

    data = await ai_actions.peek(redis, action_id)
    if data is None:
        await callback.answer(get_text("ai.action_expired", lang), show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        return
    if data.get("owner") != callback.from_user.id:
        await callback.answer(get_text("ai.action_forbidden", lang), show_alert=True)
        return

    await ai_actions.take(redis, action_id)
    await callback.answer()
    await _finish_action_message(callback, data["summary"], get_text("ai.action_cancelled", lang))


# ═══════════════════════════════════════════════════════════
# ASOSIY JARAYON
# ═══════════════════════════════════════════════════════════

async def _process_ai_text(message: Message, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    logger.info(f"[AI_HANDLER] start: user={message.from_user.id} msg_id={message.message_id}")

    lang = user_data.get("lang", "uz")
    cefr_level = user_data.get("cefr_level", "A1")
    user_message = message.text.strip()

    if not user_message or len(user_message) > MAX_TEXT_LENGTH:
        logger.debug("[AI_HANDLER] Empty or too long message")
        await message.answer(get_text("ai.error", lang))
        return

    try:
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        db_user = result.scalar_one_or_none()
        is_admin = bool(db_user and _is_admin(db_user))

        # ── Ruxsat va yoqilganlik tekshiruvlari ──
        if db_user and (not db_user.is_active or db_user.deleted_at is not None):
            await message.answer(get_text("ai.inactive", lang))
            return
        if str(settings.AI_GLOBAL_ENABLED).lower() != "true" and not is_admin:
            await message.answer(get_text("ai.global_off", lang))
            return
        if db_user and not is_admin and not db_user.ai_enabled:
            await message.answer(get_text("ai.user_off", lang))
            return

        allowed, reason = await ai_limits.check_rate_limit(message.from_user.id, is_admin)
        if not allowed:
            await message.answer(get_text("ai.rate_limited_day" if reason == "day" else "ai.rate_limited", lang))
            return

        await message.bot.send_chat_action(message.chat.id, "typing")

        if db_user:
            logger.info(f"[AI_HANDLER] Unified AI Agent (role={db_user.role})")
            await _answer_with_agent(
                message=message,
                session=session,
                db_user=db_user,
                lang=lang,
                cefr_level=cefr_level,
                user_prompt=user_message,
            )
        else:
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

    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("[AI AGENT ERROR]")
        await message.answer(get_text("ai.error", lang))
