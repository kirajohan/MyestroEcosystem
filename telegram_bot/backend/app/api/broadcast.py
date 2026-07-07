"""Broadcast API endpoints — Create and manage broadcast campaigns.

Phase 3: Admin-only endpoints for creating broadcasts and checking history.
- POST /broadcast/send — Create new broadcast job with HTML support
- GET /broadcast/history — Get all broadcasts
- GET /broadcast/{broadcast_id} — Get broadcast details with delivery stats
- GET /broadcast/{broadcast_id}/history — Get delivery history
"""

import json
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException
from redis import Redis

from app.models.user import User
from app.database import get_db
from app.config import settings
from app.core.deps import require_admin
import redis as redis_lib

logger = logging.getLogger(__name__)


def get_redis() -> Redis:
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=True)


router = APIRouter(prefix="/broadcast", tags=["broadcast"])


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
    target_all_users: bool = True  # True = all users, False = specific IDs
    target_user_ids: Optional[List[int]] = None  # Specific user IDs (if not target_all)


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
    
    def get_filtered_user_ids(self, target_all: bool, target_ids: Optional[List[int]] = None) -> List[int]:
        """Get telegram_id list based on target criteria."""
        if not target_all and target_ids:
            # Verify all target IDs exist
            query = select(User.id).where(User.id.in_(target_ids))
            result = self.db.execute(query)
            found_ids = [row[0] for row in result.fetchall()]
            return found_ids
        
        # Get all active users
        query = select(User.id).where(
            and_(
                User.id.isnot(None),
                User.deleted_at.is_(None),
            )
        )
        result = self.db.execute(query)
        return [row[0] for row in result.fetchall()]
    
    def create_broadcast(self, request: BroadcastCreate, admin_id: int) -> dict:
        """Create broadcast job and queue it in Redis."""
        import uuid
        
        broadcast_id = str(uuid.uuid4())
        
        # 1. Get target users
        user_ids = self.get_filtered_user_ids(request.target_all_users, request.target_user_ids)
        total_users = len(user_ids)
        
        if total_users == 0:
            raise ValueError("No users match the target criteria")
        
        # 2. Create progress tracking key in Redis
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
        
        # 3. Queue job for broadcast worker
        job_content = {
            "title": request.title,
            "content": request.content,
            "message_type": request.message_type,
            "file_id": request.file_id,
        }
        
        # Send as single job (not batched) — worker handles rate limiting
        job = {
            "id": broadcast_id,
            "user_ids": user_ids,
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


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.post("/send", response_model=dict)
async def send_broadcast(
    request: BroadcastCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    redis: Redis = Depends(get_redis),
):
    """Create broadcast job and queue for delivery (admin only).
    
    Returns broadcast_id for tracking progress.
    """
    try:
        service = BroadcastService(redis, db)
        result = service.create_broadcast(request, admin.id)
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
    admin: User = Depends(require_admin),
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


@router.get("/history", response_model=List[dict])
async def get_broadcast_history(
    limit: int = 50,
    redis: Redis = Depends(get_redis),
    admin: User = Depends(require_admin),
):
    """Get recent broadcasts (admin only)."""
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
