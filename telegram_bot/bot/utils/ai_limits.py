"""
AI agent uchun Redis asosidagi umumiy yordamchilar:
 - umumiy Redis klient (har xabarga yangi ulanish ochilmaydi)
 - rate-limit (daqiqa / kun)
 - dublikat xabarni filtrlash
 - foydalanuvchi bo'yicha "band" lock (ko'p instansiyada ham ishlaydi)
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from redis.asyncio import Redis

from bot.config import settings

logger = logging.getLogger(__name__)

_redis: Optional[Redis] = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


# ───────────────────────────────────────────────────────────
# Rate limit
# ───────────────────────────────────────────────────────────

async def check_rate_limit(user_id: int, is_admin: bool) -> Tuple[bool, Optional[str]]:
    """
    (ruxsat, sabab) qaytaradi. sabab: "minute" | "day" | None.
    Redis ishlamasa — so'rovni o'tkazib yuboradi (fail-open), lekin log yozadi.
    """
    per_min = settings.AI_ADMIN_RATE_PER_MINUTE if is_admin else settings.AI_RATE_PER_MINUTE
    per_day = settings.AI_ADMIN_RATE_PER_DAY if is_admin else settings.AI_RATE_PER_DAY
    day = datetime.now(timezone.utc).strftime("%Y%m%d")

    try:
        r = get_redis()
        min_key = f"ai_rl:min:{user_id}"
        day_key = f"ai_rl:day:{user_id}:{day}"

        min_count = await r.incr(min_key)
        if min_count == 1:
            await r.expire(min_key, 60)
        day_count = await r.incr(day_key)
        if day_count == 1:
            await r.expire(day_key, 86400)

        if day_count > per_day:
            return False, "day"
        if min_count > per_min:
            return False, "minute"
    except Exception as e:
        logger.warning(f"[AI-LIMIT] Redis xatosi, limit o'tkazib yuborildi: {type(e).__name__}")
    return True, None


# ───────────────────────────────────────────────────────────
# Dedup + busy lock
# ───────────────────────────────────────────────────────────

async def mark_handled(chat_id: int, message_id: int) -> bool:
    """Xabar birinchi marta ko'rilsa True (Redis SET NX)."""
    try:
        ok = await get_redis().set(f"ai_seen:{chat_id}:{message_id}", "1", nx=True, ex=300)
        return bool(ok)
    except Exception as e:
        logger.warning(f"[AI-LIMIT] dedup Redis xatosi: {type(e).__name__}")
        return True


async def acquire_busy(user_id: int, ttl: int) -> bool:
    try:
        return bool(await get_redis().set(f"ai_busy:{user_id}", "1", nx=True, ex=ttl))
    except Exception as e:
        logger.warning(f"[AI-LIMIT] busy Redis xatosi: {type(e).__name__}")
        return True


async def release_busy(user_id: int) -> None:
    try:
        await get_redis().delete(f"ai_busy:{user_id}")
    except Exception:
        pass
