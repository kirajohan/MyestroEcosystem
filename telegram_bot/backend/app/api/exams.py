"""Exams API — CRUD for CEFR tests and questions.

Endpoints:
- GET    /exams                    — list exams (optional level filter)
- POST   /exams                    — create exam
- GET    /exams/{exam_id}          — get exam detail
- PUT    /exams/{exam_id}          — update exam
- DELETE /exams/{exam_id}          — delete exam
- GET    /exams/{exam_id}/questions — list questions for exam
- POST   /exams/{exam_id}/questions — add question to exam
- GET    /test/questions?level=X   — bot endpoint: fetch questions by CEFR level
- POST   /test/attempts            — bot endpoint: save test attempt
"""

import logging
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_db
from app.models import Exam, ExamSection, ExamQuestion, ExamAttempt
from app.schemas.exam import (
    ExamCreate,
    ExamResponse,
    ExamQuestionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exams", tags=["exams"])


# ══════════════════════════════════════════════════════════════
# SCHEMAS (local)
# ══════════════════════════════════════════════════════════════

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cefr_level: Optional[str] = None
    status: Optional[str] = None
    total_duration: Optional[int] = None
    passing_score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    is_active: Optional[bool] = None


class QuestionOption(BaseModel):
    label: str
    is_correct: bool = False


class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1)
    question_type: str = "multiple_choice"
    options: Optional[List[QuestionOption]] = None
    correct_answer: str = ""
    explanation: Optional[str] = None
    points: Decimal = Decimal("1.00")
    difficulty: str = "medium"
    order_index: int = 0


class TestAttemptCreate(BaseModel):
    user_id: int
    level: str
    correct_answers: int
    total_questions: int
    percentage: float


# ══════════════════════════════════════════════════════════════
# EXAM CRUD
# ══════════════════════════════════════════════════════════════

@router.get("", response_model=List[ExamResponse])
def get_exams(
    level: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get all exams with optional CEFR level filter."""
    query = select(Exam).where(Exam.deleted_at.is_(None)).order_by(Exam.created_at.desc())

    if level:
        query = query.where(Exam.cefr_level == level.upper())

    query = query.offset(offset).limit(limit)
    result = db.execute(query)
    exams = result.scalars().all()
    return exams


@router.post("", response_model=ExamResponse, status_code=201)
def create_exam(
    payload: ExamCreate,
    db: Session = Depends(get_db),
):
    """Create a new exam."""
    exam = Exam(
        title=payload.title,
        description=payload.description,
        cefr_level=payload.cefr_level.upper(),
        status=payload.status,
        total_duration=payload.total_duration,
        reading_duration=payload.reading_duration,
        listening_duration=payload.listening_duration,
        speaking_duration=payload.speaking_duration,
        writing_duration=payload.writing_duration,
        ownership_type=payload.ownership_type,
        passing_score=payload.passing_score,
        max_score=payload.max_score,
        is_sample=payload.is_sample,
        attempt_limit=payload.attempt_limit,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    logger.info(f"✅ Exam created: id={exam.id}, title={exam.title}")
    return exam


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
):
    """Get exam by ID."""
    exam = db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    payload: ExamUpdate,
    db: Session = Depends(get_db),
):
    """Update exam details."""
    exam = db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key == "cefr_level" and value:
            value = value.upper()
        setattr(exam, key, value)

    exam.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(exam)
    logger.info(f"✅ Exam updated: id={exam.id}")
    return exam


@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
):
    """Soft-delete an exam."""
    exam = db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    exam.deleted_at = datetime.utcnow()
    exam.is_active = False
    db.commit()
    logger.info(f"🗑️ Exam deleted (soft): id={exam_id}")
    return {"status": "deleted", "exam_id": exam_id}


# ══════════════════════════════════════════════════════════════
# QUESTIONS
# ══════════════════════════════════════════════════════════════

@router.get("/{exam_id}/questions", response_model=List[ExamQuestionResponse])
def get_exam_questions(
    exam_id: int,
    db: Session = Depends(get_db),
):
    """Get all questions for an exam."""
    exam = db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    questions = db.execute(
        select(ExamQuestion)
        .join(ExamSection, ExamQuestion.section_id == ExamSection.id)
        .where(ExamSection.exam_id == exam_id)
        .order_by(ExamQuestion.order_index, ExamQuestion.id)
    ).scalars().all()

    return questions


@router.post("/{exam_id}/questions", response_model=ExamQuestionResponse, status_code=201)
def create_question(
    exam_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
):
    """Add a question to an exam.

    If the exam has no sections yet, a default section is created.
    """
    exam = db.execute(
        select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    ).scalar_one_or_none()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    # Find or create a default section
    section = db.execute(
        select(ExamSection)
        .where(ExamSection.exam_id == exam_id)
        .order_by(ExamSection.order_index)
        .limit(1)
    ).scalar_one_or_none()

    if not section:
        section = ExamSection(
            exam_id=exam_id,
            section_type="multiple_choice",
            title="Asosiy savollar",
            description="Test savollari",
            duration_minutes=exam.total_duration or 30,
            order_index=0,
            total_questions=0,
        )
        db.add(section)
        db.flush()

    # Count existing questions for order_index
    existing_count = db.execute(
        select(func.count(ExamQuestion.id))
        .join(ExamSection, ExamQuestion.section_id == ExamSection.id)
        .where(ExamSection.exam_id == exam_id)
    ).scalar() or 0

    # Build options JSONB
    options_json = None
    if payload.options:
        options_json = [
            {"label": opt.label, "is_correct": opt.is_correct}
            for opt in payload.options
        ]

    question = ExamQuestion(
        section_id=section.id,
        question_number=existing_count + 1,
        question_type=payload.question_type,
        question_text=payload.question_text,
        options=options_json,
        correct_answer=payload.correct_answer or "",
        explanation=payload.explanation,
        points=payload.points,
        difficulty=payload.difficulty,
        order_index=payload.order_index or existing_count,
    )
    db.add(question)

    # Update section total_questions
    section.total_questions = existing_count + 1

    db.commit()
    db.refresh(question)
    logger.info(f"✅ Question created: id={question.id}, exam_id={exam_id}")
    return question


# ══════════════════════════════════════════════════════════════
# BOT ENDPOINTS
# ══════════════════════════════════════════════════════════════

@router.get("/test/questions", include_in_schema=False)
def get_test_questions(
    level: str = Query(..., description="CEFR level: A1, A2, B1, B2, C1, C2"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Bot endpoint — fetch questions for a given CEFR level.

    Returns a flat list of questions with options.
    """
    level = level.upper()
    if level not in ("A1", "A2", "B1", "B2", "C1", "C2"):
        raise HTTPException(status_code=400, detail="Invalid CEFR level")

    # Find active exam for this level
    exam = db.execute(
        select(Exam)
        .where(
            Exam.cefr_level == level,
            Exam.is_active.is_(True),
            Exam.deleted_at.is_(None),
        )
        .order_by(Exam.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if not exam:
        return []

    # Get questions
    questions = db.execute(
        select(ExamQuestion)
        .join(ExamSection, ExamQuestion.section_id == ExamSection.id)
        .where(ExamSection.exam_id == exam.id)
        .order_by(ExamQuestion.order_index, ExamQuestion.id)
        .limit(limit)
    ).scalars().all()

    # Format for bot
    result = []
    for q in questions:
        options = []
        if q.options:
            for opt in q.options:
                options.append({
                    "label": opt.get("label", ""),
                    "is_correct": opt.get("is_correct", False),
                })
        result.append({
            "id": q.id,
            "question": q.question_text,
            "options": options,
            "level": level,
        })

    return result


@router.post("/test/attempts", include_in_schema=False)
def save_test_attempt(
    payload: TestAttemptCreate,
    db: Session = Depends(get_db),
):
    """Bot endpoint — save a test attempt result."""
    # Find exam for this level
    exam = db.execute(
        select(Exam)
        .where(
            Exam.cefr_level == payload.level.upper(),
            Exam.deleted_at.is_(None),
        )
        .order_by(Exam.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    if not exam:
        # Create a placeholder exam if none exists
        exam = Exam(
            title=f"CEFR {payload.level.upper()} Test",
            description="Avtomatik yaratilgan test",
            cefr_level=payload.level.upper(),
            status="published",
            total_duration=30,
            is_active=True,
        )
        db.add(exam)
        db.flush()

    # Count existing attempts
    attempt_count = db.execute(
        select(func.count(ExamAttempt.id)).where(
            ExamAttempt.exam_id == exam.id,
            ExamAttempt.user_id == payload.user_id,
        )
    ).scalar() or 0

    attempt = ExamAttempt(
        exam_id=exam.id,
        user_id=payload.user_id,
        attempt_number=attempt_count + 1,
        status="completed",
        submitted_at=datetime.utcnow(),
        total_score=Decimal(str(payload.percentage)),
        cefr_result=payload.level.upper(),
        passed=payload.percentage >= float(exam.passing_score or 60),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    logger.info(f"✅ Test attempt saved: user={payload.user_id}, level={payload.level}, score={payload.percentage}%")
    return {
        "status": "saved",
        "attempt_id": attempt.id,
        "exam_id": exam.id,
        "passed": attempt.passed,
    }
