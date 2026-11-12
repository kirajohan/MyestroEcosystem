from typing import List, Optional
from app.core.deps import require_admin, get_current_user
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from app.database import get_db
from app.schemas.user import UserResponse, UserAIToggleRequest
from app.schemas.conversation import ThreadResponse
from app.models.user import User
from app.models.conversation import ConversationThread
from app.core.exceptions import NotFoundException
from app.schemas.user import UsersListResponse
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UsersListResponse, dependencies=[Depends(require_admin)])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: DBSession = Depends(get_db),
):
    users = db.query(User).filter(User.deleted_at.is_(None)).offset(skip).limit(limit).all()
    total = db.query(User).filter(User.deleted_at.is_(None)).count()
    return {"data": [UserResponse.model_validate(u) for u in users], "total": total}


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def get_user(
    user_id: int,
    db: DBSession = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    return UserResponse.model_validate(user)


@router.get("/{user_id}/chats", response_model=List[ThreadResponse], dependencies=[Depends(require_admin)])
def get_user_chats(
    user_id: int,
    db: DBSession = Depends(get_db),
):
    threads = db.query(ConversationThread).filter(
        ConversationThread.user_id == user_id,
        ConversationThread.is_active == True,
    ).all()
    return [ThreadResponse.model_validate(t) for t in threads]


@router.put("/{user_id}/ai-toggle", response_model=UserResponse, dependencies=[Depends(require_admin)])
def toggle_user_ai(
    user_id: int,
    request: UserAIToggleRequest,
    db: DBSession = Depends(get_db),
):
    """Toggle AI enabled/disabled for a specific user."""
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")

    user.ai_enabled = request.ai_enabled
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
def update_me(
    request: dict,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update current user's profile (faqat o'zining; rol o'zgartirib bo'lmaydi)."""
    user = db.query(User).filter(User.id == current_user.id, User.is_active == True).first()
    if not user:
        raise NotFoundException("User not found")

    # DIQQAT: "role" ataylab yo'q — foydalanuvchi o'z huquqini oshira olmasin
    allowed_fields = ["full_name", "email", "phone", "cefr_level", "target_level", "lang"]
    for field, value in request.items():
        if field in allowed_fields and hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user(
    user_id: int,
    request: dict,
    db: DBSession = Depends(get_db),
):
    """Update user fields."""
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    
    allowed_fields = ["full_name", "email", "phone", "cefr_level", "target_level", "lang", "role"]
    for field, value in request.items():
        if field in allowed_fields and hasattr(user, field):
            setattr(user, field, value)
    
    # Password alohida hash qilinadi
    if "password" in request and request["password"]:
        user.password_hash = hash_password(request["password"])
    
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(
    user_id: int,
    db: DBSession = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "User soft-deleted"}


@router.put("/{user_id}/activate", dependencies=[Depends(require_admin)])
def activate_user(
    user_id: int,
    db: DBSession = Depends(get_db),
):
    """Re-activate a previously blocked user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    user.is_active = True
    user.deleted_at = None
    db.commit()
    db.refresh(user)
    return {"message": "User activated", "user": UserResponse.model_validate(user)}
