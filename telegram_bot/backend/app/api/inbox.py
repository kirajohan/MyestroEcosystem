"""Inbox API endpoints — Admin communication with users.

FIXES:
1. Sync DB session (not async)
2. Proper error handling va validation
3. Direct imports (not inside function)
4. Background task untuk Telegram send
"""

import logging
import httpx
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field

from app.database import get_db
from app.config import settings
from app.models.inbox import InboxMessage, InboxMessageHistory
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inbox", tags=["inbox"])


# ══════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════

class InboxMessageResponse(BaseModel):
    """Inbox message response."""
    id: int
    user_id: int
    user_name: Optional[str] = None
    subject: Optional[str] = None
    user_message: str
    admin_reply: Optional[str] = None
    status: str  # new, read, replied, closed
    is_read: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class InboxHistoryItem(BaseModel):
    """Message history item."""
    id: int
    sender_id: Optional[int] = None
    sender_name: Optional[str] = None
    message_text: str
    message_type: str  # user_message, admin_reply
    created_at: str
    
    model_config = {"from_attributes": True}


class AdminReply(BaseModel):
    """Send reply to user."""
    reply: str = Field(..., min_length=1, max_length=4096)


class UpdateMessageStatus(BaseModel):
    """Update message status."""
    status: str = Field(..., pattern="^(new|read|replied|closed)$")


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.get("/messages", response_model=List[InboxMessageResponse])
def get_inbox_messages(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """Get all inbox messages (paginated).
    
    Optional filters:
    - status: 'new', 'read', 'replied', 'closed'
    """
    try:
        # Build query with eager loading for related user data
        query = (
            db.query(InboxMessage)
            .options(selectinload(InboxMessage.user))
            .order_by(desc(InboxMessage.created_at))
        )
        
        # Apply status filter if provided
        if status_filter and status_filter in ["new", "read", "replied", "closed"]:
            query = query.filter(InboxMessage.status == status_filter)
        
        # Apply pagination
        total = query.count()
        messages = query.offset(offset).limit(limit).all()
        
        # Convert to response format
        response = []
        for msg in messages:
            user_name = msg.user.full_name if msg.user and msg.user.full_name else "Unknown"
            
            response.append(InboxMessageResponse(
                id=msg.id,
                user_id=msg.user_id,
                user_name=user_name,
                subject=msg.subject,
                user_message=msg.user_message,
                admin_reply=msg.admin_reply,
                status=msg.status,
                is_read=msg.is_read,
                created_at=msg.created_at.isoformat() if msg.created_at else "",
                updated_at=msg.updated_at.isoformat() if msg.updated_at else "",
            ))
        
        logger.info(f"✅ Fetched {len(messages)} inbox messages (status={status}, total={total})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error fetching inbox messages: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch inbox messages: {str(e)}"
        )


@router.get("/messages/{message_id}")
def get_message_thread(
    message_id: int,
    db: Session = Depends(get_db),
):
    """Get full message thread with history."""
    try:
        # Get main message with eager-loaded user
        msg = (
            db.query(InboxMessage)
            .options(selectinload(InboxMessage.user))
            .filter(InboxMessage.id == message_id)
            .first()
        )
        
        if not msg:
            logger.warning(f"Message {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Mark as read
        if not msg.is_read:
            msg.is_read = True
            msg.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"✅ Marked message {message_id} as read")
        
        # Get history
        history = (
            db.query(InboxMessageHistory)
            .options(selectinload(InboxMessageHistory.sender))
            .filter(InboxMessageHistory.inbox_message_id == message_id)
            .order_by(InboxMessageHistory.created_at)
            .all()
        )
        
        # Convert history to response format
        history_items = []
        for item in history:
            sender_name = "Unknown"
            
            if item.sender_id and item.sender_id > 0:
                sender_name = item.sender.full_name if item.sender and item.sender.full_name else "Unknown"
            elif item.sender_id == 0 or item.sender_id is None:
                sender_name = "🤖 Admin System" if item.message_type == "admin_reply" else "User"
            
            history_items.append(InboxHistoryItem(
                id=item.id,
                sender_id=item.sender_id,
                sender_name=sender_name,
                message_text=item.message_text,
                message_type=item.message_type,
                created_at=item.created_at.isoformat() if item.created_at else "",
            ))
        
        logger.info(f"✅ Fetched thread for message {message_id} (history: {len(history_items)} items)")
        
        return {
            "message": InboxMessageResponse(
                id=msg.id,
                user_id=msg.user_id,
                user_name=msg.user.full_name if msg.user else "Unknown",
                subject=msg.subject,
                user_message=msg.user_message,
                admin_reply=msg.admin_reply,
                status=msg.status,
                is_read=msg.is_read,
                created_at=msg.created_at.isoformat() if msg.created_at else "",
                updated_at=msg.updated_at.isoformat() if msg.updated_at else "",
            ).model_dump(),
            "history": [h.model_dump() for h in history_items],
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching thread {message_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch thread: {str(e)}"
        )


@router.post("/messages/{message_id}/reply")
def send_reply(
    message_id: int,
    payload: AdminReply,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Send admin reply to user.
    
    Reply will be:
    1. Stored in inbox_message_history
    2. Sent to user via Telegram (background task)
    3. Message status updated to 'replied'
    """
    try:
        # Validate input
        if not payload.reply or not payload.reply.strip():
            raise HTTPException(status_code=400, detail="Reply text cannot be empty")
        
        # Get inbox message
        msg = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
        
        if not msg:
            logger.warning(f"Message {message_id} not found for reply")
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Create history entry
        history_entry = InboxMessageHistory(
            inbox_message_id=message_id,
            sender_id=None,  # System/admin (no specific user)
            message_text=payload.reply.strip(),
            message_type="admin_reply",
        )
        db.add(history_entry)
        
        # Update main message
        msg.admin_reply = payload.reply.strip()
        msg.status = "replied"
        msg.updated_at = datetime.utcnow()
        
        # Commit database changes
        db.commit()
        
        logger.info(f"✅ Reply stored for message {message_id}")
        
        # Send to user via Telegram (background task)
        background_tasks.add_task(
            send_telegram_reply,
            user_id=msg.user_id,
            subject=msg.subject or "Admin Javob",
            admin_reply=payload.reply.strip(),
            message_id=message_id,
        )
        
        return {
            "status": "queued",
            "message_id": message_id,
            "reply": payload.reply[:100] + "..." if len(payload.reply) > 100 else payload.reply,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "✅ Reply stored and queued to send to user via Telegram"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to send reply for message {message_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send reply: {str(e)}"
        )


@router.patch("/messages/{message_id}/status")
def update_message_status(
    message_id: int,
    payload: UpdateMessageStatus,
    db: Session = Depends(get_db),
):
    """Update message status (read, closed, etc)."""
    try:
        msg = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
        
        if not msg:
            logger.warning(f"Message {message_id} not found for status update")
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Validate status value
        valid_statuses = ["new", "read", "replied", "closed"]
        if payload.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        msg.status = payload.status
        msg.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Message {message_id} status updated to {payload.status}")
        
        return {
            "status": "updated",
            "message_id": message_id,
            "new_status": payload.status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to update status for message {message_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update status: {str(e)}"
        )


@router.get("/stats")
def get_inbox_stats(db: Session = Depends(get_db)):
    """Get inbox statistics."""
    try:
        total = db.query(InboxMessage).count()
        new = db.query(InboxMessage).filter(InboxMessage.status == "new").count()
        replied = db.query(InboxMessage).filter(InboxMessage.status == "replied").count()
        closed = db.query(InboxMessage).filter(InboxMessage.status == "closed").count()
        unread = db.query(InboxMessage).filter(InboxMessage.is_read == False).count()
        
        logger.info(f"✅ Fetched inbox stats: total={total}, new={new}, replied={replied}, closed={closed}")
        
        return {
            "total": total,
            "new": new,
            "replied": replied,
            "closed": closed,
            "unread": unread,
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching inbox stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}"
        )


@router.delete("/messages/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
):
    """Delete message from inbox."""
    try:
        msg = db.query(InboxMessage).filter(InboxMessage.id == message_id).first()
        
        if not msg:
            logger.warning(f"Message {message_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Message not found")
        
        db.delete(msg)  # Cascade delete will remove history
        db.commit()
        
        logger.info(f"✅ Message {message_id} deleted")
        
        return {
            "status": "deleted",
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to delete message {message_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )


async def send_telegram_reply(
    user_id: int,
    subject: str,
    admin_reply: str,
    message_id: int,
):
    """Send admin reply to user via Telegram Bot API.
    
    Uses HTTP call to Telegram Bot API (not aiogram instance).
    Runs as background task — no error raising.
    """
    bot_token = settings.BOT_TOKEN
    if not bot_token:
        logger.error("❌ BOT_TOKEN not configured — cannot send Telegram reply")
        return False
    
    # Format reply message
    reply_text = (
        f"<b>📨 Admin Javob</b>\n\n"
        f"<b>Mavzu:</b> {subject}\n\n"
        f"<b>Javob:</b>\n{admin_reply}\n\n"
        f"<i>Xabar ID: {message_id}</i>"
    )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            response = await client.post(url, json={
                "chat_id": user_id,
                "text": reply_text,
                "parse_mode": "HTML",
            })
            
            if response.status_code == 200:
                logger.info(f"✅ Telegram reply sent to user {user_id} (message_id={message_id})")
                return True
            else:
                error_data = response.json()
                logger.error(f"❌ Telegram API error for user {user_id}: {error_data}")
                return False
                
    except httpx.TimeoutException:
        logger.error(f"❌ Telegram API timeout for user {user_id}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram reply to user {user_id}: {str(e)}", exc_info=True)
        return False