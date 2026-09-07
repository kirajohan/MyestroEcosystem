"""
Maestro Exam — Auth (Session-based, telefon + parol).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ Faqat SHU IMPORTLAR o'zgartirildi — hamma narsa app.database dan
from app.database import get_async_db, get_redis
from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.services.telegram_auth_service import TelegramAuthService

from app.core.security import verify_password
from app.core.session_deps import (
    SESSION_COOKIE,
    extract_session_token,
    get_current_user_from_session,
)
from app.models.user import User
from app.schemas.exam import PhoneLoginRequest, TelegramLoginResponse, UserBrief
from app.services import session_service
from app.services.session_service import SESSION_TTL_SECONDS
from app.services.telegram_webapp_service import TelegramWebAppService


logger = logging.getLogger(__name__)

router = APIRouter()


def normalize_phone(phone: str) -> str:
    digits = "".join(c for c in str(phone) if c.isdigit())
    if not digits:
        return ""
    if digits.startswith("998") and len(digits) == 12:
        return "+" + digits
    if len(digits) == 9:
        return "+998" + digits
    return "+" + digits


def _user_brief(user: User) -> UserBrief:
    return UserBrief(
        id=user.id,
        full_name=user.full_name,
        telegram_id=user.telegram_id,
        telegram_username=user.telegram_username,
        cefr_level=user.cefr_level,
        avatar_url=user.avatar_url,
        role=user.role,
    )





class WebAppLoginRequest(BaseModel):
    init_data: str


@router.post("/telegram/webapp")
async def webapp_login(
    response: Response,
    payload: WebAppLoginRequest,
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis),
):
    """Telegram Mini App initData orqali kirish."""
    
    # 1. initData validatsiyasi
    telegram_user = TelegramWebAppService.validate_init_data(payload.init_data)
    
    if not telegram_user:
        raise HTTPException(
            status_code=401,
            detail="Telegram autentifikatsiyasi muvaffaqiyatsiz",
        )

    # 2. User topish/yaratish
    user = await TelegramAuthService.get_or_create_user(db, telegram_user)

    # 3. Session yaratish va cookie o'rnatish
    token = await session_service.create_session(redis, user.id)

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=True,  # HTTPS uchun
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )

    return {
        "status": "ok",
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "full_name": user.full_name,
            "username": user.telegram_username,
            "avatar_url": user.avatar_url,
            "cefr_level": user.cefr_level,
        },
    }



@router.post(
    "/login",
    response_model=TelegramLoginResponse,
    summary="Telefon + parol orqali kirish",
)
async def login(
    payload: PhoneLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_async_db),     # ✅ get_db emas, get_async_db
    redis: Redis = Depends(get_redis),
):
    phone = normalize_phone(payload.phone)
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telefon raqam noto'g'ri formatda",
        )

    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon yoki parol noto'g'ri",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telefon yoki parol noto'g'ri",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisob faol emas",
        )

    token = await session_service.create_session(redis, user.id)

    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )

    logger.info("User logged in via phone: id=%s", user.id)

    return TelegramLoginResponse(
        access_token=token,
        refresh_token="",
        token_type="session",
        user=_user_brief(user),
    )

class TelegramLoginRequest(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

@router.post("/telegram/login")
async def telegram_login(
    response: Response,
    payload: TelegramLoginRequest,
    db: AsyncSession = Depends(get_async_db),
    redis: Redis = Depends(get_redis),
):
    """Telegram Login Widget orqali kirish"""
    
    # 1. Hash validation
    data = payload.model_dump()
    if not TelegramAuthService.verify_telegram_hash(data):
        raise HTTPException(
            status_code=401,
            detail="Telegram autentifikatsiyasi muvaffaqiyatsiz"
        )

    # 2. User topish/yaratish
    user = await TelegramAuthService.get_or_create_user(db, data)

    # 3. Session yaratish va cookie o'rnatish
    token = await session_service.create_session(redis, user.id)

    # HttpOnly cookie o'rnatamiz
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=False,  # Production: True
        samesite="lax",
        max_age=SESSION_TTL_SECONDS,
        path="/",
    )

    return {
        "status": "ok",
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "full_name": user.full_name,
            "username": user.telegram_username,
            "avatar_url": user.avatar_url,
            "cefr_level": user.cefr_level,
            "role": user.role,
        },
    }


@router.post("/logout", summary="Chiqish")
async def logout(
    request: Request,
    response: Response,
    redis: Redis = Depends(get_redis),
):
    token = extract_session_token(request)
    if token:
        await session_service.delete_session(redis, token)
    response.delete_cookie(key=SESSION_COOKIE, path="/")
    return {"detail": "Muvaffaqiyatli chiqdingiz"}


@router.get("/me", response_model=UserBrief, summary="Joriy foydalanuvchi")
async def get_me(current_user: User = Depends(get_current_user_from_session)):
    return _user_brief(current_user)
