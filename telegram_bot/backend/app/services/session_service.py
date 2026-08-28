"""Server-side session boshqaruvi (Redis asosida).

JWT o'rniga: tasodifiy opaque token Redis da saqlanadi.
Bu "JWT siz" ishlashning eng xavfsiz va sodda yo'li.
"""

import secrets
from typing import Optional

from redis.asyncio import Redis

SESSION_PREFIX = "maestro:session:"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 kun


def generate_session_token() -> str:
    """Kriptografik xavfsiz tasodifiy token."""
    return secrets.token_urlsafe(32)


async def create_session(redis: Redis, user_id: int) -> str:
    """Yangi sessiya yaratadi, token qaytaradi."""
    token = generate_session_token()
    key = f"{SESSION_PREFIX}{token}"
    await redis.setex(key, SESSION_TTL_SECONDS, str(user_id))
    return token


async def get_session_user_id(redis: Redis, token: str) -> Optional[int]:
    """Token bo'yicha user_id qaytaradi (yoki None)."""
    if not token:
        return None
    value = await redis.get(f"{SESSION_PREFIX}{token}")
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


async def refresh_session(redis: Redis, token: str) -> None:
    """Sessiya TTL ni yangilaydi (sliding expiry)."""
    if token:
        await redis.expire(f"{SESSION_PREFIX}{token}", SESSION_TTL_SECONDS)


async def delete_session(redis: Redis, token: str) -> None:
    """Sessiyani o'chiradi (logout)."""
    if token:
        await redis.delete(f"{SESSION_PREFIX}{token}")