from typing import List, Optional
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


@router.get("", response_model=UsersListResponse)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    cefr_level: Optional[str] = Query(None),
    lang: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: DBSession = Depends(get_db),
):
    query = db.query(User).filter(User.deleted_at.is_(None))
    
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(like_pattern)) | (User.email.ilike(like_pattern))
        )
    if role:
        query = query.filter(User.role == role)
    if cefr_level:
        query = query.filter(User.cefr_level == cefr_level)
    if lang:
        query = query.filter(User.lang == lang)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return {"data": [UserResponse.model_validate(u) for u in users], "total": total}


@router.get("/ids", response_model=dict)
def list_user_ids(
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    cefr_level: Optional[str] = Query(None),
    lang: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: DBSession = Depends(get_db),
):
    """Get filtered user IDs (for broadcast targeting)."""
    query = db.query(User.id).filter(User.deleted_at.is_(None))
    
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(like_pattern)) | (User.email.ilike(like_pattern))
        )
    if role:
        query = query.filter(User.role == role)
    if cefr_level:
        query = query.filter(User.cefr_level == cefr_level)
    if lang:
        query = query.filter(User.lang == lang)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    ids = [row[0] for row in query.all()]
    return {"user_ids": ids, "total": len(ids)}


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: DBSession = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")
    return UserResponse.model_validate(user)


@router.get("/{user_id}/chats", response_model=List[ThreadResponse])
def get_user_chats(
    user_id: int,
    db: DBSession = Depends(get_db),
):
    threads = db.query(ConversationThread).filter(
        ConversationThread.user_id == user_id,
        ConversationThread.is_active == True,
    ).all()
    return [ThreadResponse.model_validate(t) for t in threads]


@router.put("/{user_id}/ai-toggle", response_model=UserResponse)
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
):
    """Update current user's profile."""
    user = db.query(User).filter(User.is_active == True).first()
    if not user:
        raise NotFoundException("User not found")

    allowed_fields = ["full_name", "email", "phone", "cefr_level", "target_level", "lang", "role"]
    for field, value in request.items():
        if field in allowed_fields and hasattr(user, field):
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
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


@router.delete("/{user_id}")
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


@router.put("/{user_id}/activate")
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
