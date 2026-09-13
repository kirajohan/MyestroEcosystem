"""
User AI query handler.
Oddiy user o'z ma'lumotlari haqida so'rashi mumkin.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.services.admin_ai_service import AIToolsService
from app.services.ai_agent import AIAgent

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("mydata"))
async def cmd_my_data(message: Message, session: AsyncSession):
    """/mydata [savol] — O'z ma'lumotlarim haqida so'rash."""
    text = message.text[7:].strip() if len(message.text) > 7 else ""
    if not text:
        await message.answer(
            "📊 <b>Mening ma'lumotlarim</b>\n\n"
            "Ishlatish: <code>/mydata Nima haqida bilmoqchisiz?</code>\n\n"
            "<b>Misollar:</b>\n"
            "• <code>/mydata Mening natijalarim qanday?</code>\n"
            "• <code>/mydata Eng yaxshi skill'im qaysi?</code>\n"
            "• <code>/mydata Qaysi exam'ni topshirishim kerak?</code>\n"
            "• <code>/mydata Zaif tomonlarim nima?</code>",
            parse_mode="HTML",
        )
        return

    loading = await message.answer("🤔 Ma'lumotlaringizni tahlil qilayapman...")

    try:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        current_user = result.scalar_one_or_none()

        if not current_user:
            await loading.edit_text("❌ Siz ro'yxatdan o'tmagansiz.")
            return

        tools_service = AIToolsService(
            db=session,
            current_user_id=current_user.id,
            is_admin=False,  # USER
        )
        agent = AIAgent(tools_service, is_admin=False)

        answer = await agent.chat(text)
        await loading.edit_text(f"🤖 <b>AI Javob:</b>\n\n{answer}", parse_mode="HTML")

    except Exception as e:
        logger.error(f"User AI error: {e}", exc_info=True)
        await loading.edit_text(f"❌ Xatolik: {str(e)}")