"""Text cache service — DB dan matnlarni yuklash va Redis ga saqlash."""

import os
import httpx
import logging
from typing import Optional, Dict, Any

from bot.utils.redis_client import (
    get_redis_client,
    get_text_cache_key,
    get_all_texts_cache_key,
    TEXT_CACHE_TTL,
)

logger = logging.getLogger(__name__)

# Backend API URL
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


async def load_texts_from_backend(lang: Optional[str] = None) -> list[Dict[str, Any]]:
    """Backend dan barcha matnlarni yuklash."""
    try:
        url = f"{API_BASE_URL}/api/bot-texts/bulk"
        params = {"lang": lang} if lang else {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Backend dan matnlarni yuklashda xatolik: {e}")
        return []


async def init_text_cache() -> int:
    """
    Bot ishga tushganda chaqiriladi (ASYNC!).
    Barcha matnlarni DB dan yuklab Redis ga saqlaydi.
    
    Returns:
        Saqlangan matnlar soni
    """
    try:
        redis_client = get_redis_client()
        
        # Avval cache ni tozalash
        redis_client.delete(get_all_texts_cache_key())
        
        # Barcha matnlarni yuklash (AWAIT — asyncio.run emas!)
        texts = await load_texts_from_backend()
        
        if not texts:
            logger.warning("Backend dan matnlar yuklanmadi, lokal fallback ishlatiladi")
            return 0
        
        # Har bir matnni cache ga saqlash
        for text_item in texts:
            cache_key = get_text_cache_key(text_item["key"], text_item["lang"])
            redis_client.setex(cache_key, TEXT_CACHE_TTL, text_item["text"])
        
        # Umumiy cache key ni belgilash
        redis_client.setex(get_all_texts_cache_key(), TEXT_CACHE_TTL, str(len(texts)))
        
        logger.info(f"✅ Text cache initialized: {len(texts)} matn")
        return len(texts)
        
    except Exception as e:
        logger.error(f"Cache initialization xatosi: {e}")
        return 0


def get_text_from_cache(key: str, lang: str) -> Optional[str]:
    """Redis cache dan matn olish."""
    try:
        redis_client = get_redis_client()
        cache_key = get_text_cache_key(key, lang)
        return redis_client.get(cache_key)
    except Exception as e:
        logger.error(f"Cache dan o'qish xatosi: {e}")
        return None


def set_text_in_cache(key: str, lang: str, text: str) -> None:
    """Matnni cache ga saqlash."""
    try:
        redis_client = get_redis_client()
        cache_key = get_text_cache_key(key, lang)
        redis_client.setex(cache_key, TEXT_CACHE_TTL, text)
    except Exception as e:
        logger.error(f"Cache ga saqlash xatosi: {e}")


def invalidate_text_cache(key: Optional[str] = None, lang: Optional[str] = None) -> None:
    """Cache invalidatsiyasi."""
    try:
        redis_client = get_redis_client()
        
        if key and lang:
            redis_client.delete(get_text_cache_key(key, lang))
        elif key:
            for l in ["uz", "ru", "en"]:
                redis_client.delete(get_text_cache_key(key, l))
        else:
            keys = redis_client.keys("bot_texts:*")
            if keys:
                redis_client.delete(*keys)
            
        logger.info("✅ Text cache invalidated")
    except Exception as e:
        logger.error(f"Cache invalidation xatosi: {e}")


async def refresh_cache() -> int:
    """Cache ni to'liq yangilash (admin panel dan chaqiriladi)."""
    return await init_text_cache()