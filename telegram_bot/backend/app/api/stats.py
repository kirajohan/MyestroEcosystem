from fastapi import APIRouter, Depends, Query
from app.core.deps import require_admin
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.schemas.stats import StatsResponse, ActivityPoint, CEFRDistribution
from app.models.user import User
from app.models.conversation import Message
from app.models.logs import ErrorLog
from app.models.user import User as UserModel

# ✅ Exam modellarini import qilish
from app.models.exam import (
    Exam,
    ExamAttempt,
    ExamAIJob,
    ExamMedia,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse, dependencies=[Depends(require_admin)])
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


@router.get("/activity", response_model=list, dependencies=[Depends(require_admin)])
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


@router.get("/cefr", response_model=CEFRDistribution, dependencies=[Depends(require_admin)])
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


# ══════════════════════════════════════════════════════════════
# ✅ YANGI: DASHBOARD ENDPOINT
# ══════════════════════════════════════════════════════════════

@router.get("/dashboard", dependencies=[Depends(require_admin)])
def get_dashboard_stats(
    db: DBSession = Depends(get_db),
):
    """Dashboard uchun to'liq statistika (real ma'lumotlar)."""

    # ── 1. Asosiy statistika ──────────────────────────────────
    total_users = db.query(func.count(UserModel.id)).scalar() or 0
    total_exams = db.query(func.count(Exam.id)).scalar() or 0
    total_attempts = db.query(func.count(ExamAttempt.id)).scalar() or 0
    completed_attempts = db.query(func.count(ExamAttempt.id)).filter(
        ExamAttempt.status == "completed"
    ).scalar() or 0
    total_media = db.query(func.count(ExamMedia.id)).scalar() or 0

    # Faol foydalanuvchilar (7 kun)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_users_7d = db.query(func.count(func.distinct(Message.user_id))).filter(
        Message.created_at >= week_ago
    ).scalar() or 0

    # Bugungi xabarlar
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_messages = db.query(func.count(Message.id)).filter(
        Message.created_at >= today_start
    ).scalar() or 0

    # ── 2. AI Jobs holati ─────────────────────────────────────
    ai_jobs = {
        "pending": db.query(func.count(ExamAIJob.id)).filter(
            ExamAIJob.status == "pending"
        ).scalar() or 0,
        "processing": db.query(func.count(ExamAIJob.id)).filter(
            ExamAIJob.status == "processing"
        ).scalar() or 0,
        "completed": db.query(func.count(ExamAIJob.id)).filter(
            ExamAIJob.status == "completed"
        ).scalar() or 0,
        "error": db.query(func.count(ExamAIJob.id)).filter(
            ExamAIJob.status == "error"
        ).scalar() or 0,
    }

    # ── 3. Oxirgi urinishlar (10 ta) ─────────────────────────
    recent_attempts = (
        db.query(ExamAttempt, UserModel, Exam)
        .join(UserModel, ExamAttempt.user_id == UserModel.id)
        .join(Exam, ExamAttempt.exam_id == Exam.id)
        .order_by(ExamAttempt.created_at.desc())
        .limit(10)
        .all()
    )

    recent_attempts_list = []
    for attempt, user, exam in recent_attempts:
        recent_attempts_list.append({
            "id": attempt.id,
            "user_name": user.full_name or user.telegram_username or f"User #{user.id}",
            "exam_title": exam.title,
            "status": attempt.status,
            "score": attempt.total_score,
            "created_at": attempt.created_at.isoformat() if attempt.created_at else None,
        })

    # ── 4. Oxirgi AI xatolari (5 ta) ─────────────────────────
    recent_errors = (
        db.query(ExamAIJob)
        .filter(ExamAIJob.status == "error")
        .order_by(ExamAIJob.updated_at.desc())
        .limit(5)
        .all()
    )

    recent_errors_list = []
    for job in recent_errors:
        recent_errors_list.append({
            "id": job.id,
            "job_type": job.job_type,
            "error_message": job.error_message[:200] if job.error_message else "Unknown error",
            "attempts_count": job.attempts_count,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        })

    # ── 5. Exam turlari bo'yicha statistika ───────────────────
    exam_type_stats = (
        db.query(Exam.exam_type, func.count(Exam.id))
        .group_by(Exam.exam_type)
        .all()
    )

    exam_type_dict = {etype: count for etype, count in exam_type_stats}

    # ── Natija ────────────────────────────────────────────────
    return {
        "stats": {
            "total_users": total_users,
            "total_exams": total_exams,
            "total_attempts": total_attempts,
            "completed_attempts": completed_attempts,
            "pending_ai_jobs": ai_jobs["pending"] + ai_jobs["processing"],
            "total_content": total_media,
            "active_users_7d": active_users_7d,
            "today_messages": today_messages,
        },
        "recent_attempts": recent_attempts_list,
        "ai_jobs": ai_jobs,
        "recent_errors": recent_errors_list,
        "exam_type_stats": exam_type_dict,
    }