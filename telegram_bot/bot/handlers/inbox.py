"""Inbox handler — Capture user messages for admin inbox."""

import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import async_session
from bot.states.registration import InboxState, RegisteredSection, StartSection
from bot.keyboards.orange_keyboard import ColoredKeyboard
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()


async def send_to_inbox(user_id: int, subject: str, message: str):
    """Store user message in inbox using async session."""
    from backend.app.models import InboxMessage, InboxMessageHistory
    
    async with async_session() as db_session:
        try:
            # 1. Create main inbox message
            inbox_msg = InboxMessage(
                user_id=user_id,
                subject=subject,
                user_message=message,
                status="new",
                is_read=False,
            )
            db_session.add(inbox_msg)
            await db_session.flush()  # Get the ID
            
            # 2. Add to history
            history = InboxMessageHistory(
                inbox_message_id=inbox_msg.id,
                sender_id=user_id,
                message_text=message,
                message_type="user_message",
            )
            db_session.add(history)
            await db_session.commit()
            
            logger.info(f"✅ Message from user {user_id} stored in inbox: {subject}")
            
            # 3. Notify admin (optional)
            try:
                from bot.services.inbox_service import notify_admin_new_message
                from bot.config import ADMIN_ID
                from bot.main import bot
                
                if ADMIN_ID and ADMIN_ID > 0:
                    await notify_admin_new_message(
                        admin_id=ADMIN_ID,
                        user_id=user_id,
                        user_name="User",
                        subject=subject,
                        message=message,
                        message_id=inbox_msg.id,
                        bot=bot,
                    )
            except Exception as e:
                logger.warning(f"Could not notify admin: {e}")
            
            return inbox_msg.id
            
        except Exception as e:
            logger.error(f"Failed to store message in inbox: {e}")
            await db_session.rollback()
            return None


@router.message(Command("inbox"))
async def cmd_inbox_start(message: types.Message, state: FSMContext):
    """Start sending message to admin."""
    await message.answer(
        "📨 <b>Admin ga xabar yuboring</b>\n\n"
        "Iltimos, xabar mavzusini yozing:",
        parse_mode="HTML"
    )
    await state.set_state(InboxState.waiting_for_subject)


@router.message(InboxState.waiting_for_subject)
async def inbox_get_subject(message: types.Message, state: FSMContext):
    """Get subject from user."""
    await state.update_data(subject=message.text)
    await message.answer(
        "Endi xabar matnini yozing:",
        parse_mode="HTML"
    )
    await state.set_state(InboxState.waiting_for_message)


@router.message(InboxState.waiting_for_message)
async def inbox_get_message(
    message: types.Message, 
    state: FSMContext,
):
    """Get message and store in inbox."""
    data = await state.get_data()
    subject = data.get("subject", "No subject")
    
    # Store in database using async session
    inbox_id = await send_to_inbox(
        user_id=message.from_user.id,
        subject=subject,
        message=message.text,
    )
    
    if inbox_id:
        await message.answer(
            "✅ Xabar yuborildi! Admin tez orada javob beradi.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Xabar yuborilmadi. Iltimos, qayta urinib ko'ring.",
            parse_mode="HTML"
        )

    # state.clear() o'rniga to'g'ri holat o'rnatamiz (None state'ga tushib qolishining oldini olish)
    registration_complete = data.get("registration_complete", False)
    lang = data.get("lang", "uz")
    await state.clear()
    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
    else:
        await state.set_state(StartSection.main_menu)
    await state.update_data(lang=lang, registration_complete=registration_complete)

    await message.answer(
        get_text("main_menu", lang),
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
    )
