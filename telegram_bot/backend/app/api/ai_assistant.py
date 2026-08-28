"""AI assistant endpoints with memory system support."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import logging
from sqlalchemy import select
from app.models.user import User
from sqlalchemy import select, text  # <-- 'text' ni import qiling
from app.database import get_async_db, get_redis
from app.services.ai_service import ask_ai, analyze_error_logs
from app.services.ai_memory_service import AIMemoryService
from app.models.logs import ErrorLog
from app.schemas.chat_context import (
    ChatQueryWithMemoryRequest,
    ChatQueryWithMemoryResponse,
    AIMemorySessionResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-assistant", tags=["ai_assistant"])


class AIQueryRequest(BaseModel):
    prompt: str
    chat_history: Optional[List[Dict[str, str]]] = None
    system_prompt: Optional[str] = None


class AIQueryResponse(BaseModel):
    response: str


# ═══════════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS (backwards compatible)
# ═══════════════════════════════════════════════════════════════════

@router.get("/query", response_model=AIQueryResponse)
async def query_ai(
    prompt: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Legacy: Simple AI query without memory (stateless)."""
    result = await ask_ai(prompt)
    return AIQueryResponse(response=result)


@router.post("/analyze-logs")
async def analyze_logs(
    db: AsyncSession = Depends(get_async_db),
):
    """Analyze error logs using AI to suggest causes and solutions."""

    # ...
    logs = await db.execute(
        text("SELECT id, error_type, error_message, service FROM error_logs WHERE is_fixed = FALSE LIMIT 10")
    )
    log_records = logs.fetchall()
    
    log_data = [
        {
            "id": log[0],
            "error_type": log[1],
            "error_message": log[2],
            "service": log[3],
        }
        for log in log_records
    ]
    
    results = await analyze_error_logs(log_data)

    # Update logs with analysis
    for item in results:
        if item.get("error_type") != "parse_failed":
            # Find matching log by error_type and message pattern
            for log in log_records:
                if log[1] == item.get("error_type"):
                    # Update in database (optional)
                    logger.info(f"Analysis for {log[1]}: {item.get('solution')}")

    return {"analyzed": len(results), "results": results}


# ═══════════════════════════════════════════════════════════════════
# NEW ENDPOINTS (with memory system)
# ═══════════════════════════════════════════════════════════════════

async def get_memory_service(
    db: AsyncSession = Depends(get_async_db),
    redis_client: redis.Redis = Depends(get_redis)
) -> AIMemoryService:
    """Dependency injection for AIMemoryService."""
    return AIMemoryService(db, redis_client)


from sqlalchemy import select
from app.models.user import User  # <-- User modelini import qiling

@router.post(
    "/query-with-memory",
    response_model=ChatQueryWithMemoryResponse,
    summary="Query AI with memory context",
)
async def query_with_memory(
    request: ChatQueryWithMemoryRequest,
    db: AsyncSession = Depends(get_async_db),          # <-- QO'SHILDI
    memory_service: AIMemoryService = Depends(get_memory_service),
):
    try:
        # ═══════════════════════════════════════════════════════
        # YANGI QO'SHILGAN QISM: Telegram ID → Ichki ID konvertatsiya
        # ═══════════════════════════════════════════════════════
        result = await db.execute(
            select(User.id).where(User.telegram_id == request.user_id)
        )
        internal_user_id = result.scalar_one_or_none()

        if internal_user_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"User with telegram_id={request.user_id} not found. Register first."
            )
        # ═══════════════════════════════════════════════════════

        response = await memory_service.query_with_memory(
            user_id=internal_user_id,   # <-- Telegram ID emas, ichki ID!
            user_message=request.message,
            system_prompt=request.system_prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return response

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in query_with_memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="AI query failed")

@router.get(
    "/session/{telegram_id}",  # <-- O'ZGARTIRISH: user_id emas, telegram_id
    response_model=AIMemorySessionResponse,
    summary="Get user's active AI session"
)
async def get_session(
    telegram_id: int,  # <-- O'ZGARTIRISH
    db: AsyncSession = Depends(get_async_db),          # <-- QO'SHILDI
    memory_service: AIMemoryService = Depends(get_memory_service),
):
    try:
        # 1. Telegram ID ni ichki ID ga aylantirish
        result = await db.execute(select(User.id).where(User.telegram_id == telegram_id))
        internal_user_id = result.scalar_one_or_none()

        if internal_user_id is None:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Xotira xizmatiga ichki ID ni berish
        session = await memory_service.get_or_create_session(internal_user_id)
        
        # 3. Pydantic V2 uchun to'g'ri sintaksis (qarang: 3-xatolik)
        return AIMemorySessionResponse.model_validate(session)        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session")
    
@router.post(
    "/session/{telegram_id}/clear",
    summary="Clear session memory cache"
)
async def clear_session_memory(
    telegram_id: int,  # <-- telegram_id qabul qilamiz
    db: AsyncSession = Depends(get_async_db),
    memory_service: AIMemoryService = Depends(get_memory_service),
):
    """Clear Redis cache for user's session (soft reset)."""
    try:
        # 1. Telegram ID ni ichki ID ga aylantirish
        result = await db.execute(select(User.id).where(User.telegram_id == telegram_id))
        internal_user_id = result.scalar_one_or_none()

        if internal_user_id is None:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Foydalanuvchining thread'ini topamiz
        thread = await memory_service._get_or_create_thread(internal_user_id)
        
        # 3. Xotirani thread_id orqali tozalaymiz
        success = await memory_service.clear_session_memory(thread.id)
        
        return {
            "status": "success" if success else "failed",
            "thread_id": thread.id,
            "message": "Memory cache cleared" if success else "Error clearing cache"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear session")

@router.post(
    "/cleanup-expired",
    summary="Cleanup expired sessions",
    tags=["admin"]
)
async def cleanup_expired_sessions(
    memory_service: AIMemoryService = Depends(get_memory_service),
):
    """Admin endpoint: Remove expired sessions (call from scheduler)."""
    try:
        count = await memory_service.cleanup_expired_sessions()
        return {
            "status": "success",
            "cleaned_sessions": count,
            "message": f"Cleaned {count} expired sessions"
        }
    except Exception as e:
        logger.error(f"Error in cleanup: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")