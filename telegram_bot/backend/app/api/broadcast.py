import json
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from redis import Redis
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.broadcast import BroadcastRequest, TargetAudience
from app.database import get_db
from app.config import settings
import redis as redis_lib


def get_redis() -> Redis:
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=False)


router = APIRouter(prefix="/broadcast", tags=["broadcast"])


class BroadcastService:
    def __init__(self, redis: Redis, db: Session):
        self.redis = redis
        self.db = db
        self.BATCH_SIZE = 1000
    
    def get_filtered_user_ids(self, target: TargetAudience) -> List[int]:
        """Target audience'ga mos telegram_id'larni qaytaradi"""
        query = select(User.telegram_id).where(
            and_(
                User.telegram_id.isnot(None),
                User.is_active == True,
                User.deleted_at.is_(None)
            )
        )
        
        # Filter logikasi
        if target.roles:
            query = query.where(User.role.in_(target.roles))
        
        if target.cefr_levels:
            query = query.where(User.cefr_level.in_(target.cefr_levels))
        
        if target.active:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            query = query.where(User.last_login_at >= seven_days_ago)
        
        # Agar target.all=True bo'lsa, yuqoridagi filterlar qo'llanilmaydi
        if not target.all and not target.roles and not target.cefr_levels and not target.active:
            raise ValueError("At least one target filter must be specified")
        
        result = self.db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    def create_broadcast(self, request: BroadcastRequest) -> dict:
        """Broadcast job yaratadi va Redis queue'ga yuboradi"""
        broadcast_id = str(uuid.uuid4())
        
        # 1. Userlarni filterlash
        user_ids = self.get_filtered_user_ids(request.target)
        total_users = len(user_ids)
        
        if total_users == 0:
            raise ValueError("No users match the target criteria")
        
        # 2. Progress tracking uchun Redis Hash yaratish
        progress_key = f"broadcast:{broadcast_id}:progress"
        self.redis.hset(progress_key, mapping={
            "status": "pending",
            "total": total_users,
            "sent": 0,
            "failed": 0,
            "created_at": datetime.utcnow().isoformat()
        })
        self.redis.expire(progress_key, 86400 * 7)  # 7 kun saqlanadi
        
        # 3. Batch'larga bo'lib queue'ga yuborish
        job_content = {
            "text": request.text,
            "media_type": request.media_type.value,
            "media_url": request.media_url
        }
        
        batches_sent = 0
        for i in range(0, total_users, self.BATCH_SIZE):
            batch_user_ids = user_ids[i:i + self.BATCH_SIZE]
            
            job = {
                "id": broadcast_id,
                "batch_number": batches_sent,
                "user_ids": batch_user_ids,
                "content": job_content,
                "progress_key": progress_key
            }
            
            self.redis.lpush("myestro:broadcast:queue", json.dumps(job))
            batches_sent += 1
        
        # 4. Status'ni "queued" ga o'zgartirish
        self.redis.hset(progress_key, "status", "queued")
        
        return {
            "broadcast_id": broadcast_id,
            "total_users": total_users,
            "batches": batches_sent,
            "status": "queued"
        }


@router.post("/send")
def send_broadcast(
    request: BroadcastRequest,
    db: Session = Depends(get_db),
    r: Redis = Depends(get_redis)
):
    """Send broadcast message to filtered users."""
    service = BroadcastService(r, db)
    result = service.create_broadcast(request)
    return result


@router.get("/status/{broadcast_id}")
def get_broadcast_status(
    broadcast_id: str,
    r: Redis = Depends(get_redis)
):
    """Get broadcast job status."""
    progress_key = f"broadcast:{broadcast_id}:progress"
    status = r.hgetall(progress_key)
    
    if not status:
        return {"error": "Broadcast not found"}
    
    return {
        "broadcast_id": broadcast_id,
        "status": status.get(b"status", b"").decode(),
        "total": int(status.get(b"total", 0)),
        "sent": int(status.get(b"sent", 0)),
        "failed": int(status.get(b"failed", 0)),
    }
