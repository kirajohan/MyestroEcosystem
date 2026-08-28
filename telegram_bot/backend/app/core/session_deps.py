"""Session asosidagi auth dependency (Maestro Exam uchun)."""

from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ Faqat SHU IMPORTLAR o'zgartirildi — hamma narsa app.database dan
from app.database import get_async_db, get_redis

from app.models.user import User
from app.services import session_service

SESSION_COOKIE = "maestro_session"


def extract_session_token(request: Request) -> Optional[str]:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        return token
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


async def get_current_user_from_session(
    request: Request,
    db: AsyncSession = Depends(get_async_db),    # ✅ get_db emas, get_async_db
    redis: Redis = Depends(get_redis),
) -> User:
    token = extract_session_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessiya topilmadi",
        )

    user_id = await session_service.get_session_user_id(redis, token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessiya yaroqsiz yoki muddati tugagan",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Foydalanuvchi topilmadi",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi faol emas",
        )

    await session_service.refresh_session(redis, token)
    return user