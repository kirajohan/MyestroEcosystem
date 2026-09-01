"""
Maestro Exam — User Exams endpoints.

GET  /api/v2/exam/exams              → published examlar ro'yxati
POST /api/v2/exam/exams/{id}/attempts → attempt boshlash
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.session_deps import get_current_user_from_session
from app.database import get_async_db
from app.models.exam import Exam, ExamAttempt, ExamAttemptBlock
from app.models.user import User

router = APIRouter()


@router.get("", summary="Published examlar ro'yxati")
async def list_exams(
    exam_type: Optional[str] = Query(default=None, alias="type"),   # ← alias="type" QO'SHILDI
    cefr_level: Optional[str] = Query(default=None, alias="level"), # ← ixtiyoriy
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):

    """Foydalanuvchiga faqat published examlarni qaytaradi."""

    filters = [Exam.is_published == True]

    if exam_type:
        filters.append(Exam.exam_type == exam_type.lower())
    if cefr_level:
        filters.append(Exam.cefr_level == cefr_level.upper())

    stmt = (
        select(Exam)
        .where(*filters)
        .order_by(Exam.created_at.desc())
    )
    result = await db.execute(stmt)
    exams = result.scalars().all()

    return {
        "items": [
            {
                "id": exam.id,
                "code": exam.code,
                "title": exam.title,
                "description": exam.description,
                "exam_type": exam.exam_type,
                "cefr_level": exam.cefr_level,
                "time_limit_sec": exam.time_limit_sec,
            }
            for exam in exams
        ],
        "total": len(exams),
    }


@router.post(
    "/{exam_id}/attempts",
    status_code=status.HTTP_201_CREATED,
    summary="Exam attempt boshlash",
)
async def start_attempt(
    exam_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user_from_session),
):
    """Exam uchun yangi attempt yaratadi va block'larni tayyorlaydi."""

    # Exam topish (faqat published)
    stmt = (
        select(Exam)
        .where(Exam.id == exam_id, Exam.is_published == True)
        .options(selectinload(Exam.blocks))
    )
    result = await db.execute(stmt)
    exam = result.scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam topilmadi yoki published emas")

    blocks = sorted(exam.blocks, key=lambda b: b.order)

    if not blocks:
        raise HTTPException(status_code=400, detail="Bu exam'da block'lar yo'q")

    # Deadline hisoblash
    now = datetime.now(timezone.utc)
    deadline = None
    if exam.time_limit_sec and exam.time_limit_sec > 0:
        deadline = now + timedelta(seconds=exam.time_limit_sec)

    # Attempt yaratish
    attempt = ExamAttempt(
        user_id=current_user.id,
        exam_id=exam.id,
        status="in_progress",
        started_at=now,
        deadline=deadline,
    )
    db.add(attempt)
    await db.flush()

    # Har bir block uchun attempt_block yaratish
    attempt_blocks = []
    for block in blocks:
        ab = ExamAttemptBlock(
            attempt_id=attempt.id,
            block_id=block.id,
            status="pending",
        )
        db.add(ab)
        attempt_blocks.append((ab, block))

    await db.commit()
    await db.refresh(attempt)
    for ab, _ in attempt_blocks:
        await db.refresh(ab)

    return {
        "attempt_id": attempt.id,
        "exam_id": exam.id,
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "deadline": attempt.deadline.isoformat() if attempt.deadline else None,
        "blocks": [
            {
                "attempt_block_id": ab.id,
                "block_id": block.id,
                "block_type": block.block_type,
                "title": block.title,
                "time_limit_sec": block.time_limit_sec,
                "status": ab.status,
            }
            for ab, block in attempt_blocks
        ],
    }