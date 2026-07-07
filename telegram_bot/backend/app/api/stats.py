from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.schemas.stats import StatsResponse, ActivityPoint, CEFRDistribution
from app.models.user import User
from app.models.conversation import Message
from app.models.logs import ErrorLog
from app.models.user import User as UserModel

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(
    db: DBSession = Depends(get_db),
):
    total_users = db.query(func.count(UserModel.id)).scalar() or 0
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_users_7d = db.query(func.count(func.distinct(Message.user_id))).filter(
        Message.created_at >= week_ago
    ).scalar() or 0
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_messages = db.query(func.count(Message.id)).filter(
        Message.created_at >= today_start
    ).scalar() or 0
    error_count = db.query(func.count(ErrorLog.id)).filter(
        ErrorLog.is_fixed == False
    ).scalar() or 0

    return StatsResponse(
        total_users=total_users,
        active_users_7d=active_users_7d,
        today_messages=today_messages,
        cpu_usage=0.0,
        ram_usage=0.0,
        error_count=error_count,
    )


@router.get("/activity", response_model=list)
def get_activity(
    days: int = Query(7, ge=1, le=90),
    db: DBSession = Depends(get_db),
):
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.query(
        func.date(Message.created_at).label("date"),
        func.count(Message.id).label("count"),
    ).filter(
        Message.created_at >= start_date
    ).group_by(
        func.date(Message.created_at)
    ).order_by(
        func.date(Message.created_at)
    ).all()

    return [{"date": str(r.date), "count": r.count} for r in rows]


@router.get("/cefr", response_model=CEFRDistribution)
def get_cefr_distribution(
    db: DBSession = Depends(get_db),
):
    rows = db.query(
        UserModel.cefr_level,
        func.count(UserModel.id),
    ).group_by(UserModel.cefr_level).all()

    dist = CEFRDistribution()
    for level, count in rows:
        setattr(dist, level, count)
    return dist
