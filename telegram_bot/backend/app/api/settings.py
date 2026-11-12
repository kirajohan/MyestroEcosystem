"""Settings router — global bot and AI toggle endpoints.

Phase 5: Global settings for enabling/disabling features
- GET /settings/global — Get all global settings (public, cached)
- GET /settings/global/{key} — Get specific setting
- PATCH /settings/global/{key} — Update setting (admin only)
- Legacy endpoints preserved for backward compatibility
"""

import logging
from app.core.deps import require_admin, require_service_or_admin
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from redis import Redis

from app.database import get_db
from app.models.settings import SystemSetting
from app.schemas.user import SystemSettingResponse, SystemSettingUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


def get_redis() -> Redis:
    """Get Redis client for caching settings."""
    from app.config import settings
    import redis as redis_lib
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=True)


SETTINGS_CACHE_KEY = "myestro:global_settings"
SETTINGS_CACHE_TTL = 3600


# ══════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS (kept for backward compatibility)
# ══════════════════════════════════════════════════════════════

@router.get("/ai", response_model=SystemSettingResponse)
def get_global_ai_status(
    db: Session = Depends(get_db),
):
    """Get global AI toggle status (legacy endpoint)."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "ai_global_enabled").first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.get("/ai-public")
def get_ai_global_status_public(db: Session = Depends(get_db)):
    """Get global AI toggle status (Public/Bot — no auth required, legacy endpoint)."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "ai_global_enabled").first()
    if not setting:
        return {"value": "true"}
    return {"value": setting.value}


@router.put("/ai", response_model=SystemSettingResponse, dependencies=[Depends(require_admin)])
def toggle_global_ai(
    request: SystemSettingUpdateRequest,
    db: Session = Depends(get_db),
):
    """Toggle global AI on/off (legacy endpoint)."""
    if request.value not in ("true", "false"):
        raise HTTPException(status_code=400, detail="Value must be 'true' or 'false'")

    setting = db.query(SystemSetting).filter(SystemSetting.key == "ai_global_enabled").first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    setting.value = request.value
    db.commit()
    db.refresh(setting)
    return setting


# ══════════════════════════════════════════════════════════════
# NEW PHASE 5 ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.get("/global", response_model=Dict[str, dict], dependencies=[Depends(require_admin)])
async def get_global_settings(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Get all global settings (public endpoint — no auth required, cached).
    
    Returns settings for bot middleware checks.
    Results are cached in Redis for 1 hour.
    """
    # Try cache first
    try:
        import json
        cached = redis.hgetall(SETTINGS_CACHE_KEY)
        if cached:
            logger.debug("Global settings from cache")
            result = {}
            for key, json_val in cached.items():
                result[key] = json.loads(json_val)
            return result
    except Exception as e:
        logger.warning(f"Cache error: {e}")
    
    # Get from database
    query = db.query(SystemSetting).all()
    
    response = {}
    for setting in query:
        response[setting.key] = {
            "value": setting.value,
            "description": getattr(setting, "description", None),
            "updated_at": setting.updated_at.isoformat() if hasattr(setting, "updated_at") else None,
        }
    
    # Cache if Redis is available
    try:
        for key, val_dict in response.items():
            redis.hset(
                SETTINGS_CACHE_KEY,
                key,
                json.dumps(val_dict)
            )
        redis.expire(SETTINGS_CACHE_KEY, SETTINGS_CACHE_TTL)
    except Exception as e:
        logger.warning(f"Failed to cache settings: {e}")
    
    return response


@router.get("/global/{setting_key}", response_model=dict, dependencies=[Depends(require_service_or_admin)])
async def get_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Get specific global setting (cached)."""
    # Try cache
    try:
        import json
        cached = redis.hget(SETTINGS_CACHE_KEY, setting_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache error: {e}")
    
    # Get from database
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    
    if not setting:
        # Return default value for known settings instead of 404
        defaults = {
            "BOT_ENABLED": "true",
            "AI_ENABLED": "true",
            "ai_global_enabled": "true",
        }
        if setting_key in defaults:
            return {
                "value": defaults[setting_key],
                "description": f"Default value for {setting_key}",
                "updated_at": None,
            }
        raise HTTPException(status_code=404, detail="Setting not found")
    
    result = {
        "value": setting.value,
        "description": getattr(setting, "description", None),
        "updated_at": setting.updated_at.isoformat() if hasattr(setting, "updated_at") else None,
    }
    
    return result


@router.patch("/global/{setting_key}", response_model=dict, dependencies=[Depends(require_admin)])
async def update_global_setting(
    setting_key: str,
    payload: SystemSettingUpdateRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Update global setting (admin protection via middleware)."""
    from app.core.deps import require_admin
    from app.models.user import User
    
    # Validate setting key
    valid_keys = ["BOT_ENABLED", "AI_ENABLED", "ai_global_enabled"]
    if setting_key not in valid_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid setting key. Allowed: {', '.join(valid_keys)}"
        )
    
    # Validate value
    if payload.value not in ["true", "false"]:
        raise HTTPException(
            status_code=400,
            detail="Value must be 'true' or 'false'"
        )
    
    # Get existing setting
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    # Update
    old_value = setting.value
    setting.value = payload.value
    db.commit()
    db.refresh(setting)
    
    # Invalidate cache
    try:
        redis.delete(SETTINGS_CACHE_KEY)
        logger.info(f"Global setting updated: {setting_key} {old_value} -> {payload.value}")
    except Exception as e:
        logger.warning(f"Failed to invalidate cache: {e}")
    
    return {
        "status": "updated",
        "setting_key": setting_key,
        "old_value": old_value,
        "new_value": payload.value,
        "timestamp": datetime.utcnow().isoformat(),
    }
