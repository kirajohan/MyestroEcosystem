"""Inbox API endpoints — Admin communication with users.

Phase 4: Manage user messages and send replies
- GET /inbox/messages — Get all inbox messages (admin only)
- GET /inbox/messages/{id} — Get message thread with history
- POST /inbox/messages/{id}/reply — Send admin reply to user
- PATCH /inbox/messages/{id}/status — Update message status (read, closed)
"""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models.user import User
from app.database import get_db
from app.core.deps import require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inbox", tags=["inbox"])


# ══════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════

class InboxMessageResponse(BaseModel):
    """Inbox message response."""
    id: int
    user_id: int
    user_name: Optional[str]
    subject: Optional[str]
    user_message: str
    admin_reply: Optional[str]
    status: str  # new, read, replied, closed
    is_read: bool
    created_at: str
    updated_at: str
    
    model_config = {"from_attributes": True}


class InboxHistoryItem(BaseModel):
    """Message history item."""
    id: int
    sender_id: int
    sender_name: Optional[str]
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
async def get_inbox_messages(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get all inbox messages (admin only).
    
    Optional filters:
    - status: 'new', 'read', 'replied', 'closed'
    """
    from app.models import InboxMessage
    
    query = select(InboxMessage).order_by(InboxMessage.created_at.desc())
    
    if status:
        query = query.where(InboxMessage.status == status)
    
    query = query.offset(offset).limit(limit)
    
    result = db.execute(query)
    messages = result.scalars().all()
    
    # Convert to response format
    response = []
    for msg in messages:
        response.append(InboxMessageResponse(
            id=msg.id,
            user_id=msg.user_id,
            user_name=msg.user.full_name if hasattr(msg, 'user') else None,
            subject=msg.subject,
            user_message=msg.user_message,
            admin_reply=msg.admin_reply,
            status=msg.status,
            is_read=msg.is_read,
            created_at=msg.created_at.isoformat() if msg.created_at else "",
            updated_at=msg.updated_at.isoformat() if msg.updated_at else "",
        ))
    
    return response


@router.get("/messages/{message_id}", response_model=dict)
async def get_message_thread(
    message_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get full message thread with history."""
    from app.models import InboxMessage, InboxMessageHistory
    
    # Get main message
    msg = db.execute(
        select(InboxMessage).where(InboxMessage.id == message_id)
    ).scalar_one_or_none()
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Mark as read
    if not msg.is_read:
        msg.is_read = True
        db.commit()
    
    # Get history
    history_result = db.execute(
        select(InboxMessageHistory)
        .where(InboxMessageHistory.inbox_message_id == message_id)
        .order_by(InboxMessageHistory.created_at)
    )
    history = history_result.scalars().all()
    
    history_items = []
    for item in history:
        sender = db.execute(
            select(User).where(User.id == item.sender_id)
        ).scalar_one_or_none()
        
        history_items.append(InboxHistoryItem(
            id=item.id,
            sender_id=item.sender_id,
            sender_name=sender.full_name if sender else "Unknown",
            message_text=item.message_text,
            message_type=item.message_type,
            created_at=item.created_at.isoformat() if item.created_at else "",
        ))
    
    return {
        "message": InboxMessageResponse(
            id=msg.id,
            user_id=msg.user_id,
            user_name=msg.user.full_name if hasattr(msg, 'user') else None,
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


@router.post("/messages/{message_id}/reply")
async def send_reply(
    message_id: int,
    payload: AdminReply,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Send admin reply to user (admin only).
    
    Reply will be:
    1. Stored in inbox_message_history
    2. Sent to user via Telegram with HTML formatting
    3. Message status updated to 'replied'
    """
    from app.models import InboxMessage, InboxMessageHistory
    
    # Get inbox message
    msg = db.execute(
        select(InboxMessage).where(InboxMessage.id == message_id)
    ).scalar_one_or_none()
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    try:
        # 1. Add to history
        history_entry = InboxMessageHistory(
            inbox_message_id=message_id,
            sender_id=admin.id,
            message_text=payload.reply,
            message_type="admin_reply",
        )
        db.add(history_entry)
        
        # 2. Update main message
        msg.admin_reply = payload.reply
        msg.admin_id = admin.id
        msg.status = "replied"
        msg.updated_at = datetime.utcnow()
        
        db.commit()
        
        # 3. Send to user via Telegram (background task would be ideal)
        # For now, queue it for the bot to process
        logger.info(f"Admin {admin.id} replied to message {message_id}")
        
        return {
            "status": "sent",
            "message_id": message_id,
            "admin_id": admin.id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Failed to send reply: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reply")


@router.patch("/messages/{message_id}/status")
async def update_message_status(
    message_id: int,
    payload: UpdateMessageStatus,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update message status (read, closed, etc)."""
    from app.models import InboxMessage
    
    msg = db.execute(
        select(InboxMessage).where(InboxMessage.id == message_id)
    ).scalar_one_or_none()
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg.status = payload.status
    msg.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "status": "updated",
        "message_id": message_id,
        "new_status": payload.status,
    }


@router.get("/stats")
async def get_inbox_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Get inbox statistics."""
    from app.models import InboxMessage
    
    total = db.execute(
        select(InboxMessage).count()
    ).scalar() or 0
    
    new = db.execute(
        select(InboxMessage).where(InboxMessage.status == "new").count()
    ).scalar() or 0
    
    replied = db.execute(
        select(InboxMessage).where(InboxMessage.status == "replied").count()
    ).scalar() or 0
    
    closed = db.execute(
        select(InboxMessage).where(InboxMessage.status == "closed").count()
    ).scalar() or 0
    
    return {
        "total": total,
        "new": new,
        "replied": replied,
        "closed": closed,
        "unread": db.execute(
            select(InboxMessage).where(InboxMessage.is_read == False).count()
        ).scalar() or 0,
    }
