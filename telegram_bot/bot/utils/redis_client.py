"""Redis client for bot — text cache va boshqa maqsadlar uchun."""

import os
import redis
import logging

logger = logging.getLogger(__name__)

# Redis URL (backend bilan bir xil)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cache prefix (bot text lar uchun)
TEXT_CACHE_PREFIX = "bot_texts"
TEXT_CACHE_TTL = 3600  # 1 soat (admin o'zgartirganda invalidatsiya qilinadi)


def get_redis_client() -> redis.Redis:
    """Sync Redis client yaratish."""
    return redis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )


def get_text_cache_key(key: str, lang: str) -> str:
    """Cache key yaratish: bot_texts:main_menu:uz"""
    return f"{TEXT_CACHE_PREFIX}:{key}:{lang}"


def get_all_texts_cache_key() -> str:
    """Barcha matnlar uchun umumiy cache key."""
    return f"{TEXT_CACHE_PREFIX}:all"