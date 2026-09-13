"""
Admin AI chat handler.
Admin bot'ga tabiiy tilda yozadi, AI butun DB'ni ko'rib javob beradi.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.admin_ai_service import AIToolsService
from app.services.ai_agent import AIAgent

logger = logging.getLogger(__name__)
router = Router()


async def is_admin(telegram_id: int, session: AsyncSession) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    from sqlalchemy import select
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    return user and user.role == "admin"


@router.message(Command("ask"))
async def cmd_admin_ask(message: Message, session: AsyncSession):
    """/ask [savol] — Admin AI dan so'rash."""
    if not await is_admin(message.from_user.id, session):
        await message.answer("❌ Bu buyruq faqat adminlar uchun.")
        return

    # /ask dan keyingi matnni olish
    text = message.text[4:].strip() if len(message.text) > 4 else ""
    if not text:
        await message.answer(
            "🤖 <b>Admin AI</b>\n\n"
            "Ishlatish: <code>/ask Nima haqida bilmoqchisiz?</code>\n\n"
            "<b>Misollar:</b>\n"
            "• <code>/ask Bazada nechta user bor?</code>\n"
            "• <code>/ask Oxirgi 7 kunda nechta yangi urinish bo'ldi?</code>\n"
            "• <code>/ask AI xatoliklari bormi?</code>\n"
            "• <code>/ask Eng yaxshi 5 ta user kim?</code>\n"
            "• <code>/ask Butun baza haqida ma'lumot ber</code>",
            parse_mode="HTML",
        )
        return

    # Loading xabar
    loading = await message.answer("🤔 O'ylayapman...")

    try:
        # User ID ni olish
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        current_user = result.scalar_one_or_none()

        # Tools service va agent yaratish
        tools_service = AIToolsService(
            db=session,
            current_user_id=current_user.id,
            is_admin=True,
        )
        agent = AIAgent(tools_service, is_admin=True)

        # Javob olish
        answer = await agent.chat(text)

        await loading.edit_text(f"🤖 <b>AI Javob:</b>\n\n{answer}", parse_mode="HTML")

    except Exception as e:
        logger.error(f"Admin AI error: {e}", exc_info=True)
        await loading.edit_text(f"❌ Xatolik: {str(e)}")