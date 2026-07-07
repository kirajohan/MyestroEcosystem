"""Inbox handler — Capture user messages for admin inbox.

Phase 4: Bot side
- User sends message via /admin or admin button
- Message stored in inbox_messages table
- Admin can view and reply via admin panel
"""

import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter

logger = logging.getLogger(__name__)
router = Router()


class InboxState(StatesGroup):
    """User states for inbox interaction."""
    waiting_for_subject = State()
    waiting_for_message = State()


async def send_to_inbox(user_id: int, subject: str, message: str, db_session):
    """Store user message in inbox."""
    from app.models import InboxMessage
    from sqlalchemy.orm import Session
    
    try:
        inbox_msg = InboxMessage(
            user_id=user_id,
            subject=subject,
            user_message=message,
            status="new",
            is_read=False,
        )
        
        db_session.add(inbox_msg)
        db_session.commit()
        
        logger.info(f"Message from user {user_id} stored in inbox: {subject}")
        return inbox_msg.id
        
    except Exception as e:
        logger.error(f"Failed to store message in inbox: {e}")
        db_session.rollback()
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


@router.message(StateFilter(InboxState.waiting_for_subject))
async def inbox_get_subject(message: types.Message, state: FSMContext):
    """Get subject from user."""
    await state.update_data(subject=message.text)
    await message.answer(
        "Endi xabar matnini yozing:",
        parse_mode="HTML"
    )
    await state.set_state(InboxState.waiting_for_message)


@router.message(StateFilter(InboxState.waiting_for_message))
async def inbox_get_message(
    message: types.Message, 
    state: FSMContext,
    session  # Injected from bot context
):
    """Get message and store in inbox."""
    data = await state.get_data()
    subject = data.get("subject", "No subject")
    
    # Store in database
    inbox_id = await send_to_inbox(
        user_id=message.from_user.id,
        subject=subject,
        message=message.text,
        db_session=session
    )
    
    if inbox_id:
        await message.answer(
            "✅ Xabar yuborildi! Admin tez orada javob beradi.",
            parse_mode="HTML"
        )
        logger.info(f"Message {inbox_id} sent to inbox by user {message.from_user.id}")
    else:
        await message.answer(
            "❌ Xabar yuborilmadi. Iltimos, qayta urinib ko'ring.",
            parse_mode="HTML"
        )
    
    await state.clear()
