"""Catch-all message handler — Store all user messages in inbox."""

import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from app.models import InboxMessage, InboxMessageHistory, User
from app.database import get_async_db

logger = logging.getLogger(__name__)
router = Router()


async def store_message_in_inbox(
    user_id: int,
    telegram_id: int,
    user_name: str,
    message_text: str,
    content_type: str = "text",
    file_id: str = None,
):
    """Store user message in inbox (thread system)."""
    async for db in get_async_db():
        try:
            # 1. Find or create user
            result = await db.execute(
                User.__table__.select().where(User.telegram_id == telegram_id)
            )
            user = result.first()
            
            if not user:
                # Create basic user record
                user = User(
                    telegram_id=telegram_id,
                    full_name=user_name,
                    role="user",
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            
            # 2. Find existing open thread for this user
            result = await db.execute(
                InboxMessage.__table__.select()
                .where(
                    InboxMessage.user_id == user.id,
                    InboxMessage.status.in_(["new", "read", "replied"]),
                )
                .order_by(InboxMessage.created_at.desc())
                .limit(1)
            )
            existing_thread = result.first()
            
            if existing_thread:
                # Add to existing thread (history)
                history_entry = InboxMessageHistory(
                    inbox_message_id=existing_thread.id,
                    sender_id=user.id,
                    message_text=message_text,
                    message_type="user_message",
                )
                db.add(history_entry)
                
                # Update thread status
                existing_thread.status = "new"
                existing_thread.is_read = False
                existing_thread.user_message = message_text  # Update last message
                
                thread_id = existing_thread.id
            else:
                # Create new thread
                new_thread = InboxMessage(
                    user_id=user.id,
                    subject=f"Xabar: {user_name}",
                    user_message=message_text,
                    status="new",
                    is_read=False,
                )
                db.add(new_thread)
                await db.flush()
                
                # Add first message to history
                history_entry = InboxMessageHistory(
                    inbox_message_id=new_thread.id,
                    sender_id=user.id,
                    message_text=message_text,
                    message_type="user_message",
                )
                db.add(history_entry)
                thread_id = new_thread.id
            
            await db.commit()
            
            # 3. Notify backend via Redis pub/sub
            from app.database import get_redis
            redis = get_redis()
            await redis.publish(
                "inbox:new_message",
                json.dumps({
                    "thread_id": thread_id,
                    "user_id": user.id,
                    "telegram_id": telegram_id,
                    "user_name": user_name,
                    "message": message_text,
                    "content_type": content_type,
                })
            )
            
            logger.info(f"Message stored in thread {thread_id} from user {telegram_id}")
            return thread_id
            
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            await db.rollback()
            return None


import json


# Catch all text messages (not commands, not in FSM state)
@router.message(F.text & ~F.text.startswith("/") & StateFilter(None))
async def catch_text_message(message: types.Message, state: FSMContext):
    """Catch all text messages and store in inbox."""
    if not message.from_user:
        return
    
    thread_id = await store_message_in_inbox(
        user_id=0,  # Will be resolved from telegram_id
        telegram_id=message.from_user.id,
        user_name=message.from_user.full_name or "Unknown",
        message_text=message.text,
        content_type="text",
    )
    
    if thread_id:
        await message.answer(
            "✅ Xabaringiz qabul qilindi! Admin tez orada javob beradi.",
            parse_mode="HTML"
        )


# Catch voice messages
@router.message(F.voice & StateFilter(None))
async def catch_voice_message(message: types.Message, state: FSMContext):
    """Catch voice messages and store in inbox."""
    if not message.from_user:
        return
    
    thread_id = await store_message_in_inbox(
        user_id=0,
        telegram_id=message.from_user.id,
        user_name=message.from_user.full_name or "Unknown",
        message_text="[Ovozli xabar]",
        content_type="voice",
        file_id=message.voice.file_id,
    )
    
    if thread_id:
        await message.answer("✅ Ovozli xabaringiz qabul qilindi!")


# Catch photo messages
@router.message(F.photo & StateFilter(None))
async def catch_photo_message(message: types.Message, state: FSMContext):
    """Catch photo messages and store in inbox."""
    if not message.from_user:
        return
    
    caption = message.caption or "[Rasm]"
    thread_id = await store_message_in_inbox(
        user_id=0,
        telegram_id=message.from_user.id,
        user_name=message.from_user.full_name or "Unknown",
        message_text=caption,
        content_type="photo",
        file_id=message.photo[-1].file_id,
    )
    
    if thread_id:
        await message.answer("✅ Rasmingiz qabul qilindi!")


# Catch document messages
@router.message(F.document & StateFilter(None))
async def catch_document_message(message: types.Message, state: FSMContext):
    """Catch document messages and store in inbox."""
    if not message.from_user:
        return
    
    caption = message.caption or f"[Hujjat: {message.document.file_name}]"
    thread_id = await store_message_in_inbox(
        user_id=0,
        telegram_id=message.from_user.id,
        user_name=message.from_user.full_name or "Unknown",
        message_text=caption,
        content_type="document",
        file_id=message.document.file_id,
    )
    
    if thread_id:
        await message.answer("✅ Hujjatingiz qabul qilindi!")