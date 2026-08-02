"""Broadcast API endpoints — Create and manage broadcast campaigns.

Phase 3: Admin-only endpoints for creating broadcasts and checking history.
- POST /broadcast/send — Create new broadcast job with HTML support
- GET /broadcast/history — Get all broadcasts
- GET /broadcast/{broadcast_id} — Get broadcast details with delivery stats
- GET /broadcast/{broadcast_id}/history — Get delivery history
"""

import json
import logging
import io
import re
import asyncio
import httpx
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from redis import Redis

from app.models.user import User
from app.database import get_db
from app.config import settings
from app.services.placeholder_registry import get_placeholders
import redis as redis_lib

logger = logging.getLogger(__name__)


def get_redis() -> Redis:
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=True)


router = APIRouter(prefix="/broadcast", tags=["broadcast"])

TELEGRAM_API = "https://api.telegram.org/bot"


# ══════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════

from pydantic import BaseModel, Field


class BroadcastCreate(BaseModel):
    """Create broadcast request (admin only)."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)  # HTML formatted
    message_type: str = Field(default="text", pattern="^(text|photo|video|document)$")
    file_id: Optional[str] = None  # Telegram file_id for media
    
    # Target mode — two variants:
    # 1. target_mode="manual" + target_user_ids=[1,5,19]
    # 2. target_mode="filter" + target_filter={"cefr_level":"B1","is_active":true}
    target_mode: str = Field(default="all", pattern="^(all|manual|filter)$")
    target_user_ids: Optional[List[int]] = None  # For manual mode
    target_filter: Optional[dict] = None  # For filter mode (keys: search, role, cefr_level, lang, is_active)


class BroadcastJob(BaseModel):
    """Broadcast job response."""
    id: str
    title: str
    status: str  # pending, queued, sending, completed, failed
    total_users: int
    sent_count: int
    failed_count: int
    created_at: str


# ══════════════════════════════════════════════════════════════
# SERVICE
# ══════════════════════════════════════════════════════════════

class BroadcastService:
    """Handle broadcast job creation and queuing."""
    
    def __init__(self, redis: Redis, db: Session):
        self.redis = redis
        self.db = db
        self.BATCH_SIZE = 100  # Users per batch to avoid message spam
    
    @staticmethod
    def validate_media_file_id(file_id: Optional[str], message_type: str) -> tuple[bool, Optional[str]]:
        """Validate file_id for media broadcasts.
        
        Args:
            file_id: Telegram file_id to validate
            message_type: Type of media (photo, video, document)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if message_type == "text":
            # Text broadcasts don't need file_id
            return True, None
        
        if not file_id:
            return False, f"file_id is required for {message_type} broadcasts"
        
        if not isinstance(file_id, str) or len(file_id.strip()) == 0:
            return False, "file_id must be a non-empty string"
        
        # Basic validation - Telegram file_ids are typically long alphanumeric strings
        if len(file_id) < 20:
            return False, "file_id appears too short to be valid"
        
        # Check for common invalid patterns
        invalid_patterns = ["null", "undefined", "none", "error", "failed", "invalid"]
        if file_id.lower().strip() in invalid_patterns:
            return False, f"file_id contains invalid value: {file_id}"
        
        # Reject UUID format (common bug: UUID used instead of Telegram file_id)
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', file_id, re.IGNORECASE):
            return False, "file_id appears to be a UUID, not a Telegram file_id"
        
        return True, None
    
    def get_filtered_user_ids(self, target_mode: str, target_ids: Optional[List[int]] = None, target_filter: Optional[dict] = None) -> List[int]:
        """Get telegram_id list based on target criteria."""
        query = select(User.telegram_id).where(
            and_(
                User.telegram_id.isnot(None),
                User.deleted_at.is_(None),
            )
        )
        
        if target_mode == "manual" and target_ids:
            # Verify all target IDs exist and return telegram_id (not DB id)
            subquery = select(User.telegram_id).where(
                and_(
                    User.telegram_id.isnot(None),
                    User.id.in_(target_ids),
                )
            )
            result = self.db.execute(subquery)
            found_ids = [row[0] for row in result.fetchall()]
            return found_ids
        
        elif target_mode == "filter" and target_filter:
            # Apply filter conditions
            if target_filter.get("search"):
                like_pattern = f"%{target_filter['search']}%"
                query = query.where(
                    or_(
                        User.full_name.ilike(like_pattern),
                        User.email.ilike(like_pattern),
                    )
                )
            if target_filter.get("role"):
                query = query.where(User.role == target_filter["role"])
            if target_filter.get("cefr_level"):
                query = query.where(User.cefr_level == target_filter["cefr_level"])
            if target_filter.get("lang"):
                query = query.where(User.lang == target_filter["lang"])
            if target_filter.get("is_active") is not None:
                is_active_val = target_filter["is_active"]
                if isinstance(is_active_val, str):
                    is_active_val = is_active_val.lower() == "true"
                query = query.where(User.is_active == is_active_val)
        
        # Default "all" — no additional filters, just active users with telegram_id
        
        result = self.db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    def create_broadcast(self, request: BroadcastCreate, admin_id: int) -> dict:
        """Create broadcast job and queue it in Redis."""
        broadcast_id = str(uuid.uuid4())
        
        # 1. Validate media file_id if message_type is not text
        is_valid, error_msg = self.validate_media_file_id(request.file_id, request.message_type)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 2. Get target users (returns telegram_id list)
        user_telegram_ids = self.get_filtered_user_ids(request.target_mode, request.target_user_ids, request.target_filter)
        total_users = len(user_telegram_ids)
        
        if total_users == 0:
            raise ValueError("No users match the target criteria")
        
        # 3. Create progress tracking key in Redis
        progress_key = f"broadcast:{broadcast_id}:progress"
        self.redis.hset(progress_key, mapping={
            "status": "queued",
            "total": str(total_users),
            "sent": "0",
            "failed": "0",
            "created_at": datetime.utcnow().isoformat(),
            "admin_id": str(admin_id),
            "title": request.title,
        })
        self.redis.expire(progress_key, 86400 * 7)  # 7 days
        
        # 4. ✅ MUHIM: User ma'lumotlarini Redis'ga saqlash (placeholder rendering uchun)
        # Worker user:{telegram_id}:data hash'ini o'qiydi
        self._save_user_data_to_redis(user_telegram_ids)
        
        # 5. Queue job for broadcast worker
        # Worker expects: { content, message_type, media_url, file_id }
        job_content = {
            "content": request.content,       # Worker: content.get("content")
            "message_type": request.message_type,  # Worker: content.get("message_type")
            "media_url": request.file_id,      # Worker: content.get("media_url") — file_id = media_url
            "file_id": request.file_id,        # Worker: content.get("file_id") — Telegram file_id
        }
        
        # Send as single job (not batched) — worker handles rate limiting
        # Worker expects batch_number (we send 1 batch for all users)
        job = {
            "id": broadcast_id,
            "batch_number": 1,
            "user_ids": user_telegram_ids,
            "content": job_content,
            "progress_key": progress_key,
        }
        
        self.redis.lpush("myestro:broadcast:queue", json.dumps(job))
        
        logger.info(f"Created broadcast {broadcast_id} for {total_users} users by admin {admin_id}")
        
        return {
            "broadcast_id": broadcast_id,
            "total_users": total_users,
            "status": "queued",
        }
    
    def _save_user_data_to_redis(self, telegram_ids: List[int]) -> None:
        """✅ User ma'lumotlarini Redis'ga saqlash (placeholder rendering uchun).
        
        Bot worker user:{telegram_id}:data hash'ini o'qiydi.
        Bu ma'lumotlar placeholder'lar ({full_name}, {email}, etc.) uchun ishlatiladi.
        """
        if not telegram_ids:
            return
        
        # Get all users with their telegram_id
        query = select(User).where(
            and_(
                User.telegram_id.in_(telegram_ids),
                User.deleted_at.is_(None),
            )
        )
        result = self.db.execute(query)
        users = result.scalars().all()
        
        saved_count = 0
        for user in users:
            if not user.telegram_id:
                continue
            
            user_data = {
                "id": str(user.id),
                "email": user.email or "-",
                "full_name": user.full_name or "-",
                "role": user.role or "student",
                "cefr_level": user.cefr_level or "A1",
                "target_level": user.target_level or "A1",
                "avatar_url": user.avatar_url or "-",
                "phone": user.phone or "-",
                "lang": user.lang or "uz",
                "learning_lang": user.learning_lang or "en",
                "telegram_id": str(user.telegram_id),
                "telegram_username": user.telegram_username or "-",
                "auth_provider": user.auth_provider or "email",
                "provider_user_id": user.provider_user_id or "-",
                "is_active": str(user.is_active).lower() if user.is_active is not None else "true",
                "is_verified": str(user.is_verified).lower() if user.is_verified is not None else "false",
                "profile_completed": str(user.profile_completed).lower() if user.profile_completed is not None else "false",
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else "-",
                "location": user.location or "-",
                "ai_enabled": str(user.ai_enabled).lower() if user.ai_enabled is not None else "true",
                "created_at": user.created_at.isoformat() if user.created_at else "-",
                "updated_at": user.updated_at.isoformat() if user.updated_at else "-",
            }
            
            # Redis'ga saqlash (TTL: 1 soat)
            redis_key = f"user:{user.telegram_id}:data"
            self.redis.hset(redis_key, mapping=user_data)
            self.redis.expire(redis_key, 3600)  # 1 soat
            saved_count += 1
        
        logger.info(f"✅ Saved {saved_count} users' data to Redis for placeholder rendering")


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.post("/send", response_model=dict)
async def send_broadcast(
    request: BroadcastCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Create broadcast job and queue for delivery.
    
    Returns broadcast_id for tracking progress.
    """
    try:
        service = BroadcastService(redis, db)
        result = service.create_broadcast(request, 0)  # system admin ID
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Broadcast error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create broadcast")


@router.get("/status/{broadcast_id}", response_model=dict)
async def get_broadcast_status(
    broadcast_id: str,
    redis: Redis = Depends(get_redis),
):
    """Get broadcast job status and progress."""
    progress_key = f"broadcast:{broadcast_id}:progress"
    status = redis.hgetall(progress_key)
    
    if not status:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    
    return {
        "broadcast_id": broadcast_id,
        "title": status.get("title", ""),
        "status": status.get("status", "unknown"),
        "total": int(status.get("total", 0)),
        "sent": int(status.get("sent", 0)),
        "failed": int(status.get("failed", 0)),
        "created_at": status.get("created_at", ""),
    }


@router.post("/upload-media", response_model=dict)
async def upload_media(
    file: UploadFile = File(...),
):
    """Upload a file to Telegram storage channel and return file_id.
    
    Sends file directly to Telegram API (TELEGRAM_CONTENT_BASE channel)
    and returns the Telegram file_id immediately for use in broadcasts.
    No Redis intermediate storage, no async polling needed.
    """
    try:
        # Read file bytes
        contents = await file.read()
        file_size = len(contents)
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Determine content type
        content_type = file.content_type or "application/octet-stream"
        filename = file.filename or "upload"
        
        if not settings.BOT_TOKEN:
            raise HTTPException(status_code=400, detail="BOT_TOKEN sozlanmagan (.env)")
        if not settings.TELEGRAM_CONTENT_BASE:
            raise HTTPException(status_code=400, detail="TELEGRAM_CONTENT_BASE sozlanmagan (.env)")
        
        chat_id = settings.TELEGRAM_CONTENT_BASE
        bot_token = settings.BOT_TOKEN
        telegram_url = f"{TELEGRAM_API}{bot_token}"
        
        # Send file directly to Telegram API (with retry logic)
        file_stream = io.BytesIO(contents)
        
        max_retries = 3
        retry_delay = 1.0
        tg_resp = None
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    if content_type.startswith("image/"):
                        tg_resp = await client.post(
                            f"{telegram_url}/sendPhoto",
                            data={"chat_id": chat_id},
                            files={"photo": (filename, file_stream, content_type)},
                        )
                    elif content_type.startswith("video/"):
                        tg_resp = await client.post(
                            f"{telegram_url}/sendVideo",
                            data={"chat_id": chat_id},
                            files={"video": (filename, file_stream, content_type)},
                        )
                    else:
                        tg_resp = await client.post(
                            f"{telegram_url}/sendDocument",
                            data={"chat_id": chat_id},
                            files={"document": (filename, file_stream, content_type)},
                        )
                
                if tg_resp.status_code == 200:
                    break
                else:
                    logger.warning(f"Telegram API attempt {attempt + 1} failed: HTTP {tg_resp.status_code}")
                    
            except Exception as exc:
                logger.warning(f"Telegram API attempt {attempt + 1} error: {exc}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    # Reset stream position for retry
                    file_stream.seek(0)
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Telegram API bilan aloqa xatosi (3 attempts failed): {exc}"
                    )
        
        if not tg_resp or tg_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Telegram API xatosi: HTTP {tg_resp.status_code if tg_resp else 'No response'} — {tg_resp.text[:200] if tg_resp else 'No response'}"
            )
        
        tg_data = tg_resp.json()
        if not tg_data.get("ok"):
            error_msg = tg_data.get('description', "Noma'lum xato")
            raise HTTPException(status_code=502, detail=f"Telegram API xatosi: {error_msg}")
        
        # Extract telegram_file_id from response
        result = tg_data.get("result", {})
        if content_type.startswith("image/"):
            # Telegram returns photo as array of different sizes; largest is last
            photos = result.get("photo", [])
            telegram_file_id = photos[-1].get("file_id") if photos else None
        elif content_type.startswith("video/"):
            telegram_file_id = result.get("video", {}).get("file_id")
        else:
            telegram_file_id = result.get("document", {}).get("file_id")
        
        if not telegram_file_id:
            raise HTTPException(status_code=500, detail="Telegram javobidan file_id olinmadi")
        
        logger.info(f"Media upload completed: filename={filename}, telegram_file_id={telegram_file_id}")
        
        return {
            "upload_id": telegram_file_id,
            "telegram_file_id": telegram_file_id,
            "filename": filename,
            "content_type": content_type,
            "size": file_size,
            "status": "completed",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload media error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload media")


@router.get("/upload-status/{upload_id}", response_model=dict)
async def get_upload_status(
    upload_id: str,
):
    """Check the status of a media upload."""
    redis_conn = get_redis()
    file_key = f"upload:{upload_id}"
    data = redis_conn.hgetall(file_key)
    
    if not data:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return {
        "upload_id": upload_id,
        "filename": data.get("filename", ""),
        "content_type": data.get("content_type", ""),
        "telegram_file_id": data.get("telegram_file_id"),
        "status": data.get("status", "unknown"),
    }


@router.get("/placeholders", response_model=dict)
async def get_placeholder_list():
    """Get all available placeholders for broadcast messages."""
    placeholders = get_placeholders()
    return {"placeholders": placeholders}


@router.get("/history", response_model=List[dict])
async def get_broadcast_history(
    limit: int = 50,
    redis: Redis = Depends(get_redis),
):
    """Get recent broadcasts."""
    # Scan for all broadcast progress keys
    keys = redis.keys("broadcast:*:progress")
    
    broadcasts = []
    for key in sorted(keys, reverse=True)[:limit]:
        data = redis.hgetall(key)
        if data:
            broadcasts.append({
                "broadcast_id": key.split(":")[1],
                "title": data.get("title", ""),
                "status": data.get("status", ""),
                "total": int(data.get("total", 0)),
                "sent": int(data.get("sent", 0)),
                "failed": int(data.get("failed", 0)),
                "created_at": data.get("created_at", ""),
            })
    
    return broadcasts
