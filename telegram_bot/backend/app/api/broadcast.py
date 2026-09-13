"""Broadcast API endpoints — Create and manage broadcast campaigns. """


import json
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException
import redis as redis_lib
from redis import Redis

from app.models.user import User
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)

def get_redis() -> Redis:
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=True)

router = APIRouter(prefix="/broadcast", tags=["broadcast"])

# ══════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════
from pydantic import BaseModel, Field

class BroadcastCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    message_type: str = Field(default="text", pattern="^(text|photo|video|document)$")
    file_id: Optional[str] = None
    target_all_users: bool = True
    target_user_ids: Optional[List[int]] = None

# ══════════════════════════════════════════════════════════════
# SERVICE
# ══════════════════════════════════════════════════════════════
class BroadcastService:
    def __init__(self, redis: Redis, db: Session):
        self.redis = redis
        self.db = db
    
    def get_filtered_user_ids(self, target_all: bool, target_ids: Optional[List[int]] = None) -> List[int]:
        """
        Target filter:
        - target_all=True → barcha faol foydalanuvchilar
        - target_all=False + target_ids → faqat tanlanganlar
        - target_all=False + target_ids=None/[] → bo'sh ro'yxat (xato)
        """
        if not target_all:
            # Manual mode — faqat tanlanganlar
            if not target_ids or len(target_ids) == 0:
                logger.warning("Manual mode tanlangan, lekin target_user_ids bo'sh")
                return []  # Bo'sh ro'yxat qaytaramiz
            
            query = select(User.telegram_id).where(
                and_(User.telegram_id.isnot(None), User.id.in_(target_ids))
            )
            result = self.db.execute(query)
            return [row[0] for row in result.fetchall()]
        
        # All mode — barcha faol foydalanuvchilar
        query = select(User.telegram_id).where(
            and_(User.telegram_id.isnot(None), User.deleted_at.is_(None))
        )
        result = self.db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    def create_broadcast(self, request: BroadcastCreate, admin_id: int = 0) -> dict:
        import uuid
        broadcast_id = str(uuid.uuid4())
        user_ids = self.get_filtered_user_ids(request.target_all_users, request.target_user_ids)
        total_users = len(user_ids)
        
        if total_users == 0:
            raise ValueError("No users match the target criteria")
        
        progress_key = f"broadcast:{broadcast_id}:progress"
        self.redis.hset(progress_key, mapping={
            "status": "queued",
            "total": str(total_users),
            "sent": "0",
            "failed": "0",
            "created_at": datetime.utcnow().isoformat(),
            "admin_id": str(admin_id), # 0 = tizim tomonidan
            "title": request.title,
        })
        self.redis.expire(progress_key, 86400 * 7)
        
        job_content = {
            "content": request.content,
            "message_type": request.message_type,
            "media_url": request.file_id,
        }
        
        job = {
            "id": broadcast_id,
            "batch_number": 1,
            "user_ids": user_ids,
            "content": job_content,
            "progress_key": progress_key,
        }
        
        self.redis.lpush("myestro:broadcast:queue", json.dumps(job))
        logger.info(f"Created broadcast {broadcast_id} for {total_users} users (System/Admin {admin_id})")
        
        return {
            "broadcast_id": broadcast_id,
            "total_users": total_users,
            "status": "queued",
        }

# ══════════════════════════════════════════════════════════════
# ENDPOINTS (JWT tekshiruvisiz)
# ══════════════════════════════════════════════════════════════

@router.post("/send", response_model=dict)
async def send_broadcast(
    request: BroadcastCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    try:
        service = BroadcastService(redis, db)
        result = service.create_broadcast(request, admin_id=0) # admin_id o'rniga 0
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

@router.get("/history", response_model=List[dict])
async def get_broadcast_history(
    limit: int = 50,
    redis: Redis = Depends(get_redis),
):
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

import os
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings

# ... (oldingi kodlar: BroadcastCreate, BroadcastService va boshqa endpointlar) ...

@router.post("/upload-media")
async def upload_broadcast_media(file: UploadFile = File(...)):
    """
    Admin paneldan kelgan media faylni Telegram'dagi maxsus kanalog (MEDIA_UPLOAD) yuklaydi
    va telegram_file_id ni qaytaradi.
    """
    # 1. Fayl hajmini tekshirish (Maksimal 50MB)
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)  # Ko'rsatkichni boshiga qaytarish

    if file_size > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(status_code=400, detail="Fayl hajmi 50MB dan oshmasligi kerak")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl nomi mavjud emas")

    # 2. Fayl turiga qarab Telegram API metodini aniqlash
    content_type = file.content_type or "application/octet-stream"
    
    if content_type.startswith("image/"):
        method = "sendPhoto"
        field_name = "photo"
    elif content_type.startswith("video/"):
        method = "sendVideo"
        field_name = "video"
    else:
        method = "sendDocument"
        field_name = "document"

    # 3. Telegram API ga so'rov yuborish uchun tayyorlash
    bot_token = settings.BOT_TOKEN
    channel_id = getattr(settings, "MEDIA_UPLOAD", None)

    if not bot_token or not channel_id:
        raise HTTPException(status_code=500, detail="Server sozlamalarida BOT_TOKEN yoki MEDIA_UPLOAD_CHANNEL_ID topilmadi")

    url = f"https://api.telegram.org/bot{bot_token}/{method}"

    # httpx uchun multipart/form-data formati
    data = {
        "chat_id": channel_id,
        "caption": f"Admin Upload: {file.filename}"  # Kanalda qaysi fayl ekanligini bilish uchun
    }
    
    files = {
        field_name: (file.filename, file.file, content_type)
    }

    # 4. HTTP so'rovni yuborish
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, data=data, files=files)
            
        result = response.json()

        if not result.get("ok"):
            error_desc = result.get("description", "Noma'lum Telegram xatosi")
            raise HTTPException(status_code=500, detail=f"Telegram yuklash xatosi: {error_desc}")

        # 5. file_id ni ajratib olish
        uploaded_file_info = result["result"][field_name]
        
        # Document uchun file_id to'g'ridan-to'g'ri, Photo/Video uchun eng yuqori sifatli variantni olamiz
        if isinstance(uploaded_file_info, list):
            telegram_file_id = uploaded_file_info[-1]["file_id"]  # Eng yuqori sifat
        else:
            telegram_file_id = uploaded_file_info["file_id"]

        return {
            "filename": file.filename,
            "content_type": content_type,
            "telegram_file_id": telegram_file_id,
            "upload_id": telegram_file_id,  # Frontend compatibility uchun
            "status": "completed",
            "file_size": file_size
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Tarmoq xatosi: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kutilmagan xatolik: {str(e)}")