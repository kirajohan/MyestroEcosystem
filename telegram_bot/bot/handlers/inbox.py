"""Inbox handler — Capture user messages for admin inbox.
Foydalanuvchi xabarlarini admin_messages jadvaliga saqlaydi.
"""

import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = Router()

from app.models.admin_message import AdminMessage
from app.models.user import User
from app.websocket.admin_ws import broadcast_inbox_update


class InboxState(StatesGroup):
    """User states for inbox interaction."""
    waiting_for_message = State()


async def save_to_admin_messages(
    user_id: int,
    telegram_id: int,
    user_name: str,
    text: str,
    content_type: str = "text",
    file_id: str = None,
    db_session: AsyncSession = None
) -> int:
    """
    Foydalanuvchi xabarini admin_messages jadvaliga saqlaydi.
    """
    try:
        admin_msg = AdminMessage(
            user_id=user_id,
            user_telegram_id=telegram_id,
            user_name=user_name,
            content_type=content_type,
            text=text if content_type == "text" else None,
            file_id=file_id,
            is_read=False,
            is_replied=False,
        )
        
        db_session.add(admin_msg)
        await db_session.commit()
        await db_session.refresh(admin_msg)
        
        # WebSocket broadcast to admin panel
        try:
            await broadcast_inbox_update("new_message", {
                "message_id": admin_msg.id,
                "user_id": user_id,
                "user_telegram_id": telegram_id,
                "user_name": user_name,
                "text": text,
                "content_type": content_type,
                "created_at": admin_msg.created_at.isoformat() if admin_msg.created_at else None,
            })
        except Exception as ws_err:
            logger.warning(f"WebSocket broadcast failed: {ws_err}")
        
        logger.info(f"Message from user {telegram_id} saved to admin_messages: id={admin_msg.id}")
        return admin_msg.id
        
    except Exception as e:
        logger.error(f"Failed to save message to admin_messages: {e}", exc_info=True)
        await db_session.rollback()
        return None


@router.message(Command("inbox"))
async def cmd_inbox_start(message: types.Message, state: FSMContext):
    """Start sending message to admin."""
    await message.answer(
        "📨 <b>Admin ga xabar yuboring</b>\n\n"
        "Xabar matnini yozing yoki media (rasm, video, ovoz) yuboring:",
        parse_mode="HTML"
    )
    await state.set_state(InboxState.waiting_for_message)


@router.message(Command("aloqa"))
async def cmd_contact(message: types.Message, state: FSMContext):
    """Alias for /inbox command."""
    await cmd_inbox_start(message, state)


# ─── Text message handler ───────────────────────────────────
@router.message(StateFilter(InboxState.waiting_for_message), F.text)
async def handle_text_message(
    message: types.Message, 
    state: FSMContext,
    session: AsyncSession
):
    """Text xabarni saqlash."""
    user = message.from_user
    
    # User ma'lumotlarini DB'dan olish
    result = await session.execute(
        select(User).where(User.telegram_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    
    user_name = user.full_name or user.username or f"User {user.id}"
    user_id = db_user.id if db_user else None
    
    msg_id = await save_to_admin_messages(
        user_id=user_id,
        telegram_id=user.id,
        user_name=user_name,
        text=message.text,
        content_type="text",
        db_session=session
    )
    
    if msg_id:
        await message.answer(
            "✅ <b>Xabar yuborildi!</b>\n\n"
            "Admin tez orada javob beradi.",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "❌ Xabar yuborilmadi. Iltimos, qayta urinib ko'ring.",
            parse_mode="HTML"
        )
    
    await state.clear()


# ─── Photo handler ──────────────────────────────────────────
@router.message(StateFilter(InboxState.waiting_for_message), F.photo)
async def handle_photo_message(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    """Photo xabarni saqlash."""
    user = message.from_user
    
    result = await session.execute(
        select(User).where(User.telegram_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    
    user_name = user.full_name or user.username or f"User {user.id}"
    user_id = db_user.id if db_user else None
    
    # Eng yuqori sifatli photo file_id
    photo = message.photo[-1]
    caption = message.caption or "📷 Rasm yuborildi"
    
    msg_id = await save_to_admin_messages(
        user_id=user_id,
        telegram_id=user.id,
        user_name=user_name,
        text=caption,
        content_type="photo",
        file_id=photo.file_id,
        db_session=session
    )
    
    if msg_id:
        await message.answer(
            "✅ <b>Rasm yuborildi!</b>\n\nAdmin tez orada javob beradi.",
            parse_mode="HTML"
        )
    
    await state.clear()


# ─── Voice handler ──────────────────────────────────────────
@router.message(StateFilter(InboxState.waiting_for_message), F.voice)
async def handle_voice_message(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    """Voice xabarni saqlash."""
    user = message.from_user
    
    result = await session.execute(
        select(User).where(User.telegram_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    
    user_name = user.full_name or user.username or f"User {user.id}"
    user_id = db_user.id if db_user else None
    
    msg_id = await save_to_admin_messages(
        user_id=user_id,
        telegram_id=user.id,
        user_name=user_name,
        text="🎤 Ovozli xabar yuborildi",
        content_type="voice",
        file_id=message.voice.file_id,
        db_session=session
    )
    
    if msg_id:
        await message.answer(
            "✅ <b>Ovozli xabar yuborildi!</b>\n\nAdmin tez orada javob beradi.",
            parse_mode="HTML"
        )
    
    await state.clear()


# ─── Video handler ──────────────────────────────────────────
@router.message(StateFilter(InboxState.waiting_for_message), F.video)
async def handle_video_message(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    """Video xabarni saqlash."""
    user = message.from_user
    
    result = await session.execute(
        select(User).where(User.telegram_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    
    user_name = user.full_name or user.username or f"User {user.id}"
    user_id = db_user.id if db_user else None
    
    caption = message.caption or "🎬 Video yuborildi"
    
    msg_id = await save_to_admin_messages(
        user_id=user_id,
        telegram_id=user.id,
        user_name=user_name,
        text=caption,
        content_type="video",
        file_id=message.video.file_id,
        db_session=session
    )
    
    if msg_id:
        await message.answer(
            "✅ <b>Video yuborildi!</b>\n\nAdmin tez orada javob beradi.",
            parse_mode="HTML"
        )
    
    await state.clear()


# ─── Document handler ───────────────────────────────────────
@router.message(StateFilter(InboxState.waiting_for_message), F.document)
async def handle_document_message(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession
):
    """Document xabarni saqlash."""
    user = message.from_user
    
    result = await session.execute(
        select(User).where(User.telegram_id == user.id)
    )
    db_user = result.scalar_one_or_none()
    
    user_name = user.full_name or user.username or f"User {user.id}"
    user_id = db_user.id if db_user else None
    
    caption = message.caption or f"📄 Fayl: {message.document.file_name}"
    
    msg_id = await save_to_admin_messages(
        user_id=user_id,
        telegram_id=user.id,
        user_name=user_name,
        text=caption,
        content_type="document",
        file_id=message.document.file_id,
        db_session=session
    )
    
    if msg_id:
        await message.answer(
            "✅ <b>Fayl yuborildi!</b>\n\nAdmin tez orada javob beradi.",
            parse_mode="HTML"
        )
    
    await state.clear()