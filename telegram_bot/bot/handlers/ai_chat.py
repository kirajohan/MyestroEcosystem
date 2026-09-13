"""
Unified AI Chat Handler
- Admin uchun: butun DB'ga kirish (40+ tool)
- User uchun: o'z ma'lumotlari (5 tool) + AI Teacher
- Bitta handler — AI o'zi hal qiladi qaysi rejimda ishlashni
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.services.admin_ai_service import AIToolsService
from app.services.ai_agent import AIAgent

from bot.utils.ai_memory_client import AIMemoryClient
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.rag_client import rag_client
from bot.utils.i18n import get_text
from bot.config import settings
from typing import Optional
from bot.states.registration import (
    StartSection, RegistrationFSM, AuthFSM, RegisterFSM, LoginFSM, 
    MenuSection, QuizSection,
)
from bot.handlers.profile import ProfileEditFSM
from bot.middlewares.ai_guard import NAVIGATION_WHITELIST

# Oldingi handler'dan utility funksiyalarni import qilish
from bot.handlers.ai_agent_utils import (
    _mark_handled,
    _answer_with_typewriter,
    MAX_TEXT_LENGTH,
)

logger = logging.getLogger(__name__)
router = Router()


async def _get_user_role(telegram_id: int, session: AsyncSession) -> tuple[Optional[int], str]:
    """
    User ID va role'ni qaytaradi.
    Returns: (user_id, role) yoki (None, "user")
    """
    try:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return user.id, user.role or "user"
    except Exception as e:
        logger.error(f"Role tekshirish xatosi: {e}")
    return None, "user"


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
async def unified_ai_handler(
    message: Message, 
    state: FSMContext,
    session: AsyncSession,
):
    """
    🎯 Unified AI Agent Handler
    
    Bitta handler — barcha matn xabarlari uchun:
    - Admin: butun DB'ga kirish (40+ tool)
    - User: o'z ma'lumotlari + AI Teacher
    - AI o'zi qaror qiladi: tool chaqirish yoki oddiy javob
    """
    
    # 🔒 Deduplication
    if not _mark_handled(message.message_id):
        logger.warning(f"[AI] Duplicate message skipped: id={message.message_id}")
        return
    
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    cefr_level = user_data.get("cefr_level", "A1")
    user_message = message.text.strip()
    
    if not user_message or len(user_message) > MAX_TEXT_LENGTH:
        await message.answer(get_text("ai.error", lang))
        return
    
    # Typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # 1. User ID va role'ni aniqlash
        db_user_id, role = await _get_user_role(message.from_user.id, session)
        
        if not db_user_id:
            # User DB'da yo'q — oddiy AI Teacher rejimi
            await _fallback_ai_teacher(message, lang, cefr_level, user_message)
            return
        
        is_admin = (role == "admin")
        
        # 2. Tools service yaratish
        tools_service = AIToolsService(
            db=session,
            current_user_id=db_user_id,
            is_admin=is_admin,
        )
        
        # 3. AI Agent yaratish
        agent = AIAgent(tools_service, is_admin=is_admin)
        
        # 4. Qo'shimcha kontekst (RAG + AI Teacher prompt)
        additional_context = await _build_additional_context(
            lang=lang,
            cefr_level=cefr_level,
            user_message=user_message,
            is_admin=is_admin,
        )
        
        # 5. Placeholder xabar yuborish (thinking animation)
        sent = await message.answer("🤔 O'ylayapman...")
        
        # 6. AI Agent'dan javob olish
        answer = await agent.chat(
            user_message=user_message,
            additional_context=additional_context,
        )
        
        # 7. Javobni formatlash va yuborish
        header = "🤖 <b>Myestro AI</b>\n\n"
        if is_admin:
            header = "👑 <b>Admin AI</b>\n\n"
        
        full_response = header + answer
        
        # Typewriter effect bilan yuborish
        await _answer_with_typewriter(sent, message, full_response)
        
    except Exception as e:
        logger.exception("[Unified AI Handler Error]")
        await message.answer(get_text("ai.error", lang))


async def _build_additional_context(
    lang: str,
    cefr_level: str,
    user_message: str,
    is_admin: bool,
) -> str:
    """AI agent uchun qo'shimcha kontekst yaratish (RAG + AI Teacher prompt)."""
    
    context_parts = []
    
    # 1. Foydalanuvchi haqida
    context_parts.append(f"Foydalanuvchi tili: {lang}")
    context_parts.append(f"Foydalanuvchi CEFR darajasi: {cefr_level}")
    context_parts.append(f"Role: {'Admin' if is_admin else 'Oddiy foydalanuvchi'}")
    
    # 2. RAG (faqat oddiy user uchun, admin uchun shart emas)
    if not is_admin:
        try:
            rag_context = await rag_client.build_context(user_message)
            if rag_context:
                context_parts.append(
                    f"📚 BILIMLAR BAZASI (RAG):\n{rag_context}\n\n"
                    f"⚠️ Agar savol bu ma'lumotlarga tegishli bo'lsa, ulardan foydalan."
                )
        except Exception as e:
            logger.warning(f"RAG xatosi: {e}")
    
    return "\n".join(context_parts)


async def _fallback_ai_teacher(
    message: Message,
    lang: str,
    cefr_level: str,
    user_message: str,
):
    """
    Fallback: User DB'da yo'q bo'lsa, oddiy AI Teacher rejimi.
    Eski _answer_with_memory funksiyasini ishlatadi.
    """
    from bot.handlers.ai_agent_utils import _answer_with_memory
    
    system_prompt = build_system_prompt(lang, cefr_level)
    
    try:
        rag_context = await rag_client.build_context(user_message)
        if rag_context:
            system_prompt += (
                f"\n\n📚 BILIMLAR BAZASI (RAG):\n{rag_context}\n\n"
                f"⚠️ Yuqoridagi BILIMLAR BAZASI ma'lumotlaridan foydalanib javob bering."
            )
    except Exception:
        pass
    
    await _answer_with_memory(
        message=message,
        lang=lang,
        system_prompt=system_prompt,
        user_prompt=user_message,
    )