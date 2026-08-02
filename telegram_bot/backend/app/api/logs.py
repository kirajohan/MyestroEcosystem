"""Logs API endpoints — Query and search application logs.

Phase 6: Admin-only log viewing and searching
- GET /logs — Get recent logs (paginated)
- GET /logs/search — Search logs by message, user, level
- GET /logs/stats — Get log statistics (errors, warnings, etc)
- GET /logs/export — Export logs as CSV/JSON
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, desc
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])


# ══════════════════════════════════════════════════════════════
# SCHEMAS
# ══════════════════════════════════════════════════════════════

class LogEntry(BaseModel):
    """Log entry response."""
    id: int
    timestamp: str
    level: str
    logger_name: Optional[str]
    message: str
    module: Optional[str]
    function_name: Optional[str]
    line_number: Optional[int]
    exception: Optional[str]
    user_id: Optional[int]
    extra_data: Optional[dict]
    
    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.get("/", response_model=List[LogEntry])
async def get_logs(
    level: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    hours: int = Query(24, ge=1, le=720),  # Last X hours
    db: Session = Depends(get_db),
):
    """Get recent logs with optional level filter.
    
    Parameters:
    - level: Filter by level (INFO, WARNING, ERROR, DEBUG, CRITICAL)
    - hours: Look back X hours (default 24)
    - limit: Results per page (1-1000)
    - offset: Pagination offset
    """
    from app.models import Log
    
    # Calculate time range
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(Log).where(Log.timestamp >= since)
    
    if level:
        query = query.where(Log.level == level.upper())
    
    query = query.order_by(desc(Log.timestamp))
    query = query.offset(offset).limit(limit)
    
    result = db.execute(query)
    logs = result.scalars().all()
    
    return [
        LogEntry(
            id=log.id,
            timestamp=log.timestamp.isoformat() if log.timestamp else "",
            level=log.level,
            logger_name=log.logger_name,
            message=log.message,
            module=log.module,
            function_name=log.function_name,
            line_number=log.line_number,
            exception=log.exception,
            user_id=log.user_id,
            extra_data=log.extra_data,
        )
        for log in logs
    ]


@router.get("/search", response_model=List[LogEntry])
async def search_logs(
    q: str = Query(..., min_length=1, max_length=255),
    level: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Search logs by message content.
    
    Parameters:
    - q: Search query (searches message and exception fields)
    - level: Optional level filter
    - limit: Max results to return
    """
    from app.models import Log
    
    # Last 7 days for search
    since = datetime.utcnow() - timedelta(days=7)
    
    query = select(Log).where(
        and_(
            Log.timestamp >= since,
            or_(
                Log.message.ilike(f"%{q}%"),
                Log.exception.ilike(f"%{q}%"),
            )
        )
    )
    
    if level:
        query = query.where(Log.level == level.upper())
    
    query = query.order_by(desc(Log.timestamp)).limit(limit)
    
    result = db.execute(query)
    logs = result.scalars().all()
    
    return [
        LogEntry(
            id=log.id,
            timestamp=log.timestamp.isoformat() if log.timestamp else "",
            level=log.level,
            logger_name=log.logger_name,
            message=log.message,
            module=log.module,
            function_name=log.function_name,
            line_number=log.line_number,
            exception=log.exception,
            user_id=log.user_id,
            extra_data=log.extra_data,
        )
        for log in logs
    ]


@router.get("/stats", response_model=dict)
async def get_log_stats(
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """Get log statistics for time period."""
    from app.models import Log
    
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total logs
    total = db.execute(
        select(Log).where(Log.timestamp >= since).count()
    ).scalar() or 0
    
    # By level
    levels = {}
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        count = db.execute(
            select(Log).where(
                and_(Log.timestamp >= since, Log.level == level)
            ).count()
        ).scalar() or 0
        if count > 0:
            levels[level] = count
    
    # By module
    modules = {}
    result = db.execute(
        select(Log.module, Log.level).where(Log.timestamp >= since)
    )
    for module, level in result.all():
        if module:
            if module not in modules:
                modules[module] = {"total": 0, "errors": 0}
            modules[module]["total"] += 1
            if level in ["ERROR", "CRITICAL"]:
                modules[module]["errors"] += 1
    
    # Get top errors
    top_errors = db.execute(
        select(Log.message).where(
            and_(Log.timestamp >= since, Log.level == "ERROR")
        ).order_by(desc(Log.timestamp)).limit(5)
    ).scalars().all()
    
    return {
        "period_hours": hours,
        "total_logs": total,
        "by_level": levels,
        "by_module": modules,
        "recent_errors": top_errors,
    }


@router.get("/user/{user_id}", response_model=List[LogEntry])
async def get_user_logs(
    user_id: int,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get logs related to specific user (admin only)."""
    from app.models import Log
    
    # Last 30 days
    since = datetime.utcnow() - timedelta(days=30)
    
    query = select(Log).where(
        and_(Log.timestamp >= since, Log.user_id == user_id)
    ).order_by(desc(Log.timestamp)).limit(limit)
    
    result = db.execute(query)
    logs = result.scalars().all()
    
    return [
        LogEntry(
            id=log.id,
            timestamp=log.timestamp.isoformat() if log.timestamp else "",
            level=log.level,
            logger_name=log.logger_name,
            message=log.message,
            module=log.module,
            function_name=log.function_name,
            line_number=log.line_number,
            exception=log.exception,
            user_id=log.user_id,
            extra_data=log.extra_data,
        )
        for log in logs
    ]
