"""Broadcast API endpoints — Create and manage broadcast campaigns."""

import json
from app.core.deps import require_admin
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

# User modeliga mos maydonlar (faqat mavjudlari)
USER_FIELDS_FOR_TEMPLATE = [
    User.id,
    User.telegram_id,
    User.full_name,
    User.telegram_username,
    User.phone,
    User.email,
    User.cefr_level,
]

BATCH_SIZE = 50


class BroadcastService:
    def __init__(self, redis: Redis, db: Session):
        self.redis = redis
        self.db = db

    def _get_target_users(self, target_all: bool, target_ids: Optional[List[int]] = None) -> List[User]:
        """Target filter — to'liq User obyektlarini qaytaradi."""
        if not target_all:
            if not target_ids:
                logger.warning("Manual mode, lekin target_user_ids bo'sh")
                return []

            query = (
                select(*USER_FIELDS_FOR_TEMPLATE)
                .where(
                    and_(
                        User.telegram_id.isnot(None),
                        User.id.in_(target_ids),
                        User.deleted_at.is_(None),
                    )
                )
            )
            result = self.db.execute(query)
            return [User(**dict(row._mapping)) for row in result.fetchall()]

        query = (
            select(*USER_FIELDS_FOR_TEMPLATE)
            .where(
                and_(
                    User.telegram_id.isnot(None),
                    User.deleted_at.is_(None),
                )
            )
        )
        result = self.db.execute(query)
        return [User(**dict(row._mapping)) for row in result.fetchall()]

    @staticmethod
    def _split_full_name(full_name: Optional[str]) -> tuple:
        """full_name'ni first_name va last_name'ga ajratadi."""
        if not full_name:
            return ("Foydalanuvchi", "")
        parts = full_name.strip().split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        return (first_name, last_name)

    @classmethod
    def _user_to_dict(cls, user: User) -> dict:
        """User obyektini worker uchun dict'ga o'tkazadi."""
        first_name, last_name = cls._split_full_name(user.full_name)
        return {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": user.full_name or "",
            "telegram_username": user.telegram_username or "",
            "phone": user.phone or "",
            "email": user.email or "",
            "cefr_level": user.cefr_level or "",
        }

    def create_broadcast(self, request: BroadcastCreate, admin_id: int = 0) -> dict:
        import uuid

        broadcast_id = str(uuid.uuid4())
        users = self._get_target_users(request.target_all_users, request.target_user_ids)
        total_users = len(users)

        if total_users == 0:
            raise ValueError("No users match the target criteria")

        progress_key = f"broadcast:{broadcast_id}:progress"
        self.redis.hset(
            progress_key,
            mapping={
                "status": "queued",
                "total": str(total_users),
                "sent": "0",
                "failed": "0",
                "created_at": datetime.utcnow().isoformat(),
                "admin_id": str(admin_id),
                "title": request.title,
            },
        )
        self.redis.expire(progress_key, 86400 * 7)

        job_content = {
            "content": request.content,
            "message_type": request.message_type,
            "media_url": request.file_id,
        }

        batches_sent = 0
        for i in range(0, total_users, BATCH_SIZE):
            batch_users = users[i : i + BATCH_SIZE]
            batch_dict = [self._user_to_dict(u) for u in batch_users]

            job = {
                "id": broadcast_id,
                "batch_number": (i // BATCH_SIZE) + 1,
                "users": batch_dict,
                "content": job_content,
                "progress_key": progress_key,
            }

            self.redis.lpush("myestro:broadcast:queue", json.dumps(job))
            batches_sent += 1

        logger.info(
            "Created broadcast %s for %d users in %d batches (admin=%s)",
            broadcast_id, total_users, batches_sent, admin_id,
        )

        return {
            "broadcast_id": broadcast_id,
            "total_users": total_users,
            "batches": batches_sent,
            "status": "queued",
        }


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════


@router.post("/send", response_model=dict, dependencies=[Depends(require_admin)])
async def send_broadcast(
    request: BroadcastCreate,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    admin: User = Depends(require_admin),
):
    try:
        service = BroadcastService(redis, db)
        logger.info("Broadcast requested by admin id=%s", admin.id)
        result = service.create_broadcast(request, admin_id=admin.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Broadcast error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create broadcast")


@router.get("/status/{broadcast_id}", response_model=dict, dependencies=[Depends(require_admin)])
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


@router.get("/history", response_model=List[dict], dependencies=[Depends(require_admin)])
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


# ══════════════════════════════════════════════════════════════
# MEDIA UPLOAD
# ══════════════════════════════════════════════════════════════
import os
import httpx
from fastapi import UploadFile, File


@router.post("/upload-media", dependencies=[Depends(require_admin)])
async def upload_broadcast_media(file: UploadFile = File(...)):
    """Admin paneldan kelgan media faylni Telegram kanalga yuklaydi."""
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fayl hajmi 50MB dan oshmasligi kerak")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl nomi mavjud emas")

    content_type = file.content_type or "application/octet-stream"

    if content_type.startswith("image/"):
        method, field_name = "sendPhoto", "photo"
    elif content_type.startswith("video/"):
        method, field_name = "sendVideo", "video"
    else:
        method, field_name = "sendDocument", "document"

    bot_token = settings.BOT_TOKEN
    channel_id = getattr(settings, "MEDIA_UPLOAD", None)

    if not bot_token or not channel_id:
        raise HTTPException(
            status_code=500,
            detail="BOT_TOKEN yoki MEDIA_UPLOAD sozlamasi topilmadi",
        )

    url = f"https://api.telegram.org/bot{bot_token}/{method}"

    data = {"chat_id": channel_id, "caption": f"Admin Upload: {file.filename}"}
    files = {field_name: (file.filename, file.file, content_type)}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, data=data, files=files)

        result = response.json()

        if not result.get("ok"):
            error_desc = result.get("description", "Telegram xatosi")
            raise HTTPException(status_code=500, detail=f"Telegram xatosi: {error_desc}")

        uploaded_file_info = result["result"][field_name]

        if isinstance(uploaded_file_info, list):
            telegram_file_id = uploaded_file_info[-1]["file_id"]
        else:
            telegram_file_id = uploaded_file_info["file_id"]

        return {
            "filename": file.filename,
            "content_type": content_type,
            "telegram_file_id": telegram_file_id,
            "upload_id": telegram_file_id,
            "status": "completed",
            "file_size": file_size,
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Tarmoq xatosi: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xatolik: {e}")


# ══════════════════════════════════════════════════════════════
# PLACEHOLDERS
# ══════════════════════════════════════════════════════════════
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession


@router.get("/placeholders", dependencies=[Depends(require_admin)])
def get_placeholders(db: DBSession = Depends(get_db)):
    """Broadcast uchun mavjud placeholder'larni qaytaradi."""

    sample_user = (
        db.query(User)
        .filter(User.is_active == True, User.telegram_id != None)  # noqa: E711,E712
        .first()
    )

    # full_name ni ajratish
    sample_first, sample_last = BroadcastService._split_full_name(
        sample_user.full_name if sample_user else None
    )

    placeholders = [
        {
            "key": "{first_name}",
            "label": "Ism",
            "description": "Foydalanuvchining ismi (full_name dan olinadi)",
            "example": sample_first,
        },
        {
            "key": "{last_name}",
            "label": "Familiya",
            "description": "Foydalanuvchining familiyasi (full_name dan olinadi)",
            "example": sample_last or "—",
        },
        {
            "key": "{full_name}",
            "label": "Toliq ism",
            "description": "Ism va familiya",
            "example": sample_user.full_name if sample_user else "Ali Valiyev",
        },
        {
            "key": "{username}",
            "label": "Username",
            "description": "Telegram username (@ bilan)",
            "example": (
                f"@{sample_user.telegram_username}"
                if sample_user and sample_user.telegram_username
                else "@ali_valiyev"
            ),
        },
        {
            "key": "{phone}",
            "label": "Telefon",
            "description": "Telefon raqami",
            "example": (
                sample_user.phone
                if sample_user and sample_user.phone
                else "+998 90 123 45 67"
            ),
        },
        {
            "key": "{email}",
            "label": "Email",
            "description": "Email manzil",
            "example": (
                sample_user.email
                if sample_user and sample_user.email
                else "ali@example.com"
            ),
        },
        {
            "key": "{cefr_level}",
            "label": "CEFR daraja",
            "description": "Ingliz tili darajasi",
            "example": (
                sample_user.cefr_level
                if sample_user and sample_user.cefr_level
                else "B1"
            ),
        },
        {
            "key": "{telegram_id}",
            "label": "Telegram ID",
            "description": "Telegram ID raqami",
            "example": str(sample_user.telegram_id) if sample_user else "123456789",
        },
        {
            "key": "{user_id}",
            "label": "User ID",
            "description": "Ichki foydalanuvchi ID",
            "example": str(sample_user.id) if sample_user else "1",
        },
    ]

    total_users = (
        db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0  # noqa: E712
    )
    total_with_telegram = (
        db.query(func.count(User.id))
        .filter(User.is_active == True, User.telegram_id != None)  # noqa: E711,E712
        .scalar()
        or 0
    )

    return {
        "placeholders": placeholders,
        "stats": {
            "total_users": total_users,
            "total_with_telegram": total_with_telegram,
        },
    }