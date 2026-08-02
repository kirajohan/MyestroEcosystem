"""Inbox Service — Send admin replies to users via Telegram.

Bot Integration:
- Admin panel'dan reply yuborilganda, user'ga Telegram xabari yuboriladi
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def send_admin_reply_to_user(
    user_id: int,
    subject: str,
    admin_reply: str,
    message_id: int,
    bot,  # aiogram Bot instance
    db: Session = None
):
    """Send admin reply to user via Telegram.
    
    Args:
        user_id: User Telegram ID
        subject: Message subject
        admin_reply: Admin's reply text
        message_id: Inbox message ID
        bot: Aiogram Bot instance
        db: Database session
    
    Returns:
        bool: True if sent successfully
    """
    try:
        # Format reply message
        reply_text = (
            f"<b>📨 Admin Javob</b>\n\n"
            f"<b>Mavzu:</b> {subject}\n\n"
            f"<b>Javob:</b>\n{admin_reply}\n\n"
            f"<i>Xabar ID: {message_id}</i>"
        )
        
        # Send to user
        await bot.send_message(
            chat_id=user_id,
            text=reply_text,
            parse_mode="HTML"
        )
        
        logger.info(f"✅ Admin reply sent to user {user_id} (message_id={message_id})")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to send admin reply to user {user_id}: {e}")
        return False


async def notify_admin_new_message(
    admin_id: int,
    user_id: int,
    user_name: str,
    subject: str,
    message: str,
    message_id: int,
    bot,
):
    """Notify admin about new user message.
    
    Args:
        admin_id: Admin Telegram ID
        user_id: User Telegram ID
        user_name: User full name
        subject: Message subject
        message: Message text
        message_id: Inbox message ID
        bot: Aiogram Bot instance
    """
    try:
        notification_text = (
            f"<b>🔔 Yangi Xabar Admin Inbox'ida</b>\n\n"
            f"<b>Foydalanuvchi:</b> {user_name} (ID: {user_id})\n"
            f"<b>Mavzu:</b> {subject}\n\n"
            f"<b>Xabar:</b>\n{message}\n\n"
            f"<b>Admin Panel'dan Javob Bering:</b>\n"
            f"/inbox_{message_id}"
        )
        
        await bot.send_message(
            chat_id=admin_id,
            text=notification_text,
            parse_mode="HTML"
        )
        
        logger.info(f"✅ Admin notification sent (message_id={message_id})")
    
    except Exception as e:
        logger.error(f"❌ Failed to notify admin: {e}")


def get_inbox_stats(db: Session) -> dict:
    """Get inbox statistics.
    
    Returns:
        dict: Statistics about inbox messages
    """
    from backend.app.models import InboxMessage
    from sqlalchemy import func
    
    try:
        total = db.execute(select(func.count(InboxMessage.id))).scalar() or 0
        new = db.execute(
            select(func.count(InboxMessage.id)).where(InboxMessage.status == "new")
        ).scalar() or 0
        replied = db.execute(
            select(func.count(InboxMessage.id)).where(InboxMessage.status == "replied")
        ).scalar() or 0
        closed = db.execute(
            select(func.count(InboxMessage.id)).where(InboxMessage.status == "closed")
        ).scalar() or 0
        unread = db.execute(
            select(func.count(InboxMessage.id)).where(InboxMessage.is_read == False)
        ).scalar() or 0
        
        return {
            "total": total,
            "new": new,
            "replied": replied,
            "closed": closed,
            "unread": unread,
        }
    except Exception as e:
        logger.error(f"Failed to get inbox stats: {e}")
        return {"total": 0, "new": 0, "replied": 0, "closed": 0, "unread": 0}
