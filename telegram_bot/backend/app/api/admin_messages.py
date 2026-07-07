"""Admin messages API — inbox for user messages sent to admin."""

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.admin_message import AdminMessage
from app.schemas.admin_message import (
    AdminMessageCreate,
    AdminMessageReply,
    AdminMessageResponse,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/admin-messages", tags=["admin_messages"])


@router.get("", response_model=List[AdminMessageResponse])
def list_messages(
    is_read: Optional[bool] = Query(None),
    db: DBSession = Depends(get_db),
):
    """List admin messages with optional filters."""
    query = db.query(AdminMessage)
    if is_read is not None:
        query = query.filter(AdminMessage.is_read == is_read)
    return query.order_by(AdminMessage.created_at.desc()).all()


@router.post("", response_model=AdminMessageResponse)
def create_message(
    data: AdminMessageCreate,
    db: DBSession = Depends(get_db),
):
    """Create a new admin message (from bot)."""
    msg = AdminMessage(**data.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.post("/{id}/reply", response_model=AdminMessageResponse)
def reply_message(
    id: int,
    data: AdminMessageReply,
    db: DBSession = Depends(get_db),
):
    """Reply to an admin message."""
    msg = db.query(AdminMessage).filter(AdminMessage.id == id).first()
    if not msg:
        raise NotFoundException(f"Message {id} not found")
    msg.admin_reply = data.reply
    msg.is_replied = True
    db.commit()
    db.refresh(msg)
    return msg


@router.post("/{id}/read", response_model=AdminMessageResponse)
def mark_read(
    id: int,
    db: DBSession = Depends(get_db),
):
    """Mark a message as read."""
    msg = db.query(AdminMessage).filter(AdminMessage.id == id).first()
    if not msg:
        raise NotFoundException(f"Message {id} not found")
    msg.is_read = True
    db.commit()
    db.refresh(msg)
    return msg
