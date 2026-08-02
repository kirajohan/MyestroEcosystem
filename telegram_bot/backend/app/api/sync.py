from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.models.conversation import ConversationThread, Message
from app.models.logs import ErrorLog
from app.core.exceptions import NotFoundException, AppException, ConflictException

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncMessageRequest(BaseModel):
    telegram_user_id: int
    thread_id: int
    role: str = "user"
    content: str
    content_type: str = "text"
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    grammar_corrections: Optional[Dict[str, Any]] = None
    vocabulary_suggestions: Optional[Dict[str, Any]] = None


class ReplyRequest(BaseModel):
    content: str
    ai_model: Optional[str] = None


class ErrorReportRequest(BaseModel):
    service: str
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    severity: str = "error"
    metadata: Optional[Dict[str, Any]] = None


@router.post("/telegram-message")
def sync_telegram_message(
    data: SyncMessageRequest,
    db: DBSession = Depends(get_db),
):
    """Sync message from Telegram Bot to Backend."""
    user = db.query(User).filter(User.telegram_id == data.telegram_user_id).first()
    if not user:
        return {"error": "User not found"}

    thread = db.query(ConversationThread).filter(
        ConversationThread.id == data.thread_id,
        ConversationThread.user_id == user.id,
    ).first()
    if not thread:
        return {"error": "Thread not found"}

    message = Message(
        thread_id=thread.id,
        user_id=user.id,
        role=data.role,
        content=data.content,
        content_type=data.content_type,
        ai_model=data.ai_model,
        tokens_used=data.tokens_used,
        grammar_corrections=data.grammar_corrections,
        vocabulary_suggestions=data.vocabulary_suggestions,
        source="telegram",
    )
    db.add(message)
    thread.last_sync_at = db.func.now()
    db.commit()

    return {"status": "synced", "message_id": message.id}


@router.post("/reply/{user_id}")
def sync_reply(
    user_id: int,
    data: ReplyRequest,
    db: DBSession = Depends(get_db),
):
    """Store AI reply to be sent to user via Bot."""
    thread = db.query(ConversationThread).filter(
        ConversationThread.user_id == user_id,
        ConversationThread.is_active == True,
    ).order_by(ConversationThread.last_sync_at.desc().nulls_last()).first()

    if not thread:
        return {"error": "No active thread found"}

    message = Message(
        thread_id=thread.id,
        user_id=user_id,
        role="assistant",
        content=data.content,
        ai_model=data.ai_model,
        source="api",
    )
    db.add(message)
    db.commit()

    return {"status": "reply_stored", "message_id": message.id}


@router.post("/error")
def sync_error(
    data: ErrorReportRequest,
    db: DBSession = Depends(get_db),
):
    """Log error from any service."""
    log = ErrorLog(
        service=data.service,
        error_type=data.error_type,
        error_message=data.error_message,
        stack_trace=data.stack_trace,
        severity=data.severity,
        metadata=data.metadata,
    )
    db.add(log)
    db.commit()

    return {"status": "logged", "error_id": log.id}


@router.get("/user/{telegram_id}")
def get_sync_user(
    telegram_id: int,
    db: DBSession = Depends(get_db),
):
    """Get user by telegram_id for bot sync. Accepts telegram_id or internal id for compatibility."""
    # Try finding by telegram_id first, fall back to internal id
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = db.query(User).filter(User.id == telegram_id).first()
    if not user:
        raise NotFoundException("User not found")
    return UserResponse.model_validate(user)


@router.post("/user")
def create_sync_user(
    data: dict,
    db: DBSession = Depends(get_db),
):
    """Create or update user from bot registration."""
    telegram_id = data.get("telegram_id")
    if not telegram_id:
        raise AppException("telegram_id required", 400)
    
    existing = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing:
        raise ConflictException("User already exists")
    
    user = User(
        telegram_id=telegram_id,
        telegram_username=data.get("telegram_username", ""),
        phone=data.get("phone", ""),
        full_name=data.get("full_name", ""),
        cefr_level=data.get("cefr_level", "A1"),
        lang=data.get("lang", "uz"),
        auth_provider=data.get("auth_provider", "telegram"),
        provider_user_id=str(telegram_id),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/users/{telegram_id}/ai-toggle")
def toggle_user_ai_sync(
    telegram_id: int,
    data: dict,
    db: DBSession = Depends(get_db),
):
    """Toggle user AI enabled/disabled from Bot (no auth required)."""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise NotFoundException("User not found")
    user.ai_enabled = data.get("ai_enabled", True)
    db.commit()
    db.refresh(user)
    return {"ai_enabled": user.ai_enabled}


@router.put("/user/{telegram_id}")
def update_sync_user(
    telegram_id: int,
    data: dict,
    db: DBSession = Depends(get_db),
):
    """Update user profile from Bot (no auth required). Allowed fields are whitelisted.
    Accepts telegram_id or internal id for compatibility with older bot state.
    """
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        # Fallback: try internal id match
        user = db.query(User).filter(User.id == telegram_id).first()
    if not user:
        raise NotFoundException("User not found")

    allowed_fields = ["full_name", "email", "phone", "cefr_level", "lang", "password"]
    from app.core.security import hash_password

    for field, value in data.items():
        if field in allowed_fields and hasattr(user, field if field != "password" else "password_hash"):
            if field == "password":
                # Hash password into password_hash column
                user.password_hash = hash_password(value)
            else:
                setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
