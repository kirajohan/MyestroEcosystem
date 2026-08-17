from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.exam import Exam, ExamSection, ExamQuestion, ExamAttempt, ExamAnswer
from app.models.user import User
from app.schemas.exam import (
    ExamCreate, ExamUpdate, ExamResponse,
    ExamSectionCreate, ExamSectionResponse,
    ExamQuestionCreate, ExamQuestionUpdate, ExamQuestionResponse,
    ExamAttemptCreate, ExamAttemptResponse,
    ExamAnswerCreate, ExamAnswerResponse,
    ExamSubmitRequest, ExamResultResponse,
)
from app.core.security import get_current_active_user

router = APIRouter(prefix="/exams", tags=["exams"])


# ══════════════════════════════════════════════════════════════
# EXAM CRUD (Admin Panel uchun)
# ══════════════════════════════════════════════════════════════

@router.get("/", response_model=List[ExamResponse])
async def get_exams(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    level: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Barcha testlar ro'yxati (pagination + filterlar)."""
    query = select(Exam).where(Exam.deleted_at.is_(None))
    
    if level:
        query = query.where(Exam.cefr_level == level)
    if status:
        query = query.where(Exam.status == status)
    
    query = query.offset(offset).limit(limit).order_by(Exam.created_at.desc())
    
    result = await db.execute(query)
    exams = result.scalars().all()
    return exams


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Bitta testni olish."""
    query = select(Exam).where(
        Exam.id == exam_id,
        Exam.deleted_at.is_(None)
    )
    result = await db.execute(query)
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    
    return exam


@router.post("/", response_model=ExamResponse, status_code=201)
async def create_exam(
    data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Yangi test yaratish."""
    exam = Exam(
        title=data.title,
        description=data.description,
        cefr_level=data.cefr_level,
        status=data.status,
        total_duration=data.total_duration,
        reading_duration=data.reading_duration,
        listening_duration=data.listening_duration,
        speaking_duration=data.speaking_duration,
        writing_duration=data.writing_duration,
        ownership_type=data.ownership_type,
        passing_score=data.passing_score,
        max_score=data.max_score,
        is_sample=data.is_sample,
        attempt_limit=data.attempt_limit,
        is_published=data.is_published,
        created_by=current_user.id,
    )
    
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    
    # Avtomatik bitta section yaratish (QUIZ uchun)
    section = ExamSection(
        exam_id=exam.id,
        section_type="quiz",
        title=f"{exam.title} - Questions",
        description=exam.description,
        duration_minutes=exam.total_duration,
        order_index=0,
    )
    db.add(section)
    await db.commit()
    
    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Testni tahrirlash."""
    query = select(Exam).where(
        Exam.id == exam_id,
        Exam.deleted_at.is_(None)
    )
    result = await db.execute(query)
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exam, key, value)
    
    await db.commit()
    await db.refresh(exam)
    
    return exam


@router.delete("/{exam_id}", response_model=ExamResponse)
async def delete_exam(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Testni o'chirish (soft delete)."""
    query = select(Exam).where(
        Exam.id == exam_id,
        Exam.deleted_at.is_(None)
    )
    result = await db.execute(query)
    exam = result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    
    exam.deleted_at = datetime.utcnow()
    await db.commit()
    await db.refresh(exam)
    
    return exam


# ══════════════════════════════════════════════════════════════
# QUESTIONS (Savollar)
# ══════════════════════════════════════════════════════════════

@router.get("/{exam_id}/questions", response_model=List[ExamQuestionResponse])
async def get_exam_questions(exam_id: int, db: AsyncSession = Depends(get_db)):
    """Testga tegishli barcha savollarni olish."""
    # Avval test borligini tekshirish
    exam_query = select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    exam_result = await db.execute(exam_query)
    exam = exam_result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    
    # Section'larni olish
    sections_query = select(ExamSection).where(ExamSection.exam_id == exam_id)
    sections_result = await db.execute(sections_query)
    sections = sections_result.scalars().all()
    
    if not sections:
        return []
    
    section_ids = [s.id for s in sections]
    
    # Savollarni olish
    questions_query = (
        select(ExamQuestion)
        .where(ExamQuestion.section_id.in_(section_ids))
        .order_by(ExamQuestion.order_index)
    )
    questions_result = await db.execute(questions_query)
    questions = questions_result.scalars().all()
    
    return questions


@router.post("/{exam_id}/questions", response_model=ExamQuestionResponse, status_code=201)
async def add_question(
    exam_id: int,
    data: ExamQuestionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Testga yangi savol qo'shish."""
    # Test borligini tekshirish
    exam_query = select(Exam).where(Exam.id == exam_id, Exam.deleted_at.is_(None))
    exam_result = await db.execute(exam_query)
    exam = exam_result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Test topilmadi")
    
    # Birinchi section'ni olish (yoki yaratish)
    section_query = select(ExamSection).where(ExamSection.exam_id == exam_id).limit(1)
    section_result = await db.execute(section_query)
    section = section_result.scalar_one_or_none()
    
    if not section:
        section = ExamSection(
            exam_id=exam_id,
            section_type="quiz",
            title=f"{exam.title} - Questions",
            description=exam.description,
            duration_minutes=exam.total_duration,
            order_index=0,
        )
        db.add(section)
        await db.flush()
    
    # Oxirgi question_number'ni olish
    max_num_query = select(func.max(ExamQuestion.question_number)).where(
        ExamQuestion.section_id == section.id
    )
    max_num_result = await db.execute(max_num_query)
    max_num = max_num_result.scalar() or 0
    
    question = ExamQuestion(
        section_id=section.id,
        question_number=max_num + 1,
        question_type=data.question_type,
        question_text=data.question_text,
        options=data.options,
        correct_answer=data.correct_answer,
        explanation=data.explanation,
        points=data.points,
        difficulty=data.difficulty,
        audio_url=data.audio_url,
        image_url=data.image_url,
        order_index=data.order_index,
    )
    
    db.add(question)
    await db.commit()
    await db.refresh(question)
    
    # Section'dagi savollar sonini yangilash
    count_query = select(func.count(ExamQuestion.id)).where(
        ExamQuestion.section_id == section.id
    )
    count_result = await db.execute(count_query)
    section.total_questions = count_result.scalar()
    await db.commit()
    
    return question


@router.put("/{exam_id}/questions/{question_id}", response_model=ExamQuestionResponse)
async def update_question(
    exam_id: int,
    question_id: int,
    data: ExamQuestionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Savolni tahrirlash."""
    query = select(ExamQuestion).where(ExamQuestion.id == question_id)
    result = await db.execute(query)
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    
    await db.commit()
    await db.refresh(question)
    
    return question


@router.delete("/{exam_id}/questions/{question_id}", status_code=204)
async def delete_question(
    exam_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Savolni o'chirish."""
    query = select(ExamQuestion).where(ExamQuestion.id == question_id)
    result = await db.execute(query)
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Savol topilmadi")
    
    section_id = question.section_id
    await db.delete(question)
    await db.commit()
    
    # Section'dagi savollar sonini yangilash
    section_query = select(ExamSection).where(ExamSection.id == section_id)
    section_result = await db.execute(section_query)
    section = section_result.scalar_one_or_none()
    
    if section:
        count_query = select(func.count(ExamQuestion.id)).where(
            ExamQuestion.section_id == section_id
        )
        count_result = await db.execute(count_query)
        section.total_questions = count_result.scalar()
        await db.commit()
    
    return None


# ══════════════════════════════════════════════════════════════
# BOT UCHUN — PUBLIC API
# ══════════════════════════════════════════════════════════════

@router.get("/public/list", response_model=List[ExamResponse])
async def get_public_exams(
    cefr_level: str = Query(...),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Bot uchun: faqat published testlar ro'yxati."""
    query = (
        select(Exam)
        .where(
            Exam.cefr_level == cefr_level,
            Exam.is_published == True,
            Exam.deleted_at.is_(None)
        )
        .offset(offset)
        .limit(limit)
        .order_by(Exam.created_at.desc())
    )
    
    result = await db.execute(query)
    exams = result.scalars().all()
    return exams


@router.post("/{exam_id}/start", response_model=ExamAttemptResponse)
async def start_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Testni boshlash (attempt yaratish)."""
    # Test borligini tekshirish
    exam_query = select(Exam).where(
        Exam.id == exam_id,
        Exam.is_published == True,
        Exam.deleted_at.is_(None)
    )
    exam_result = await db.execute(exam_query)
    exam = exam_result.scalar_one_or_none()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Test topilmadi yoki nashr etilmagan")
    
    # Attempt limit tekshirish
    attempts_count_query = select(func.count(ExamAttempt.id)).where(
        ExamAttempt.exam_id == exam_id,
        ExamAttempt.user_id == current_user.id
    )
    attempts_count_result = await db.execute(attempts_count_query)
    attempts_count = attempts_count_result.scalar()
    
    if attempts_count >= exam.attempt_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Attempt limit tugadi ({exam.attempt_limit} ta)"
        )
    
    # Yangi attempt yaratish
    attempt = ExamAttempt(
        exam_id=exam_id,
        user_id=current_user.id,
        attempt_number=attempts_count + 1,
        status="in_progress",
    )
    
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    
    return attempt


@router.post("/{exam_id}/submit", response_model=ExamResultResponse)
async def submit_exam(
    exam_id: int,
    data: ExamSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Test javoblarini yuborish va natijani hisoblash."""
    # Attempt'ni olish
    attempt_query = select(ExamAttempt).where(
        ExamAttempt.id == data.attempt_id,
        ExamAttempt.user_id == current_user.id,
        ExamAttempt.status == "in_progress"
    )
    attempt_result = await db.execute(attempt_query)
    attempt = attempt_result.scalar_one_or_none()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt topilmadi yoki tugallangan")
    
    # Javoblarni saqlash va tekshirish
    correct_count = 0
    total_score = Decimal("0.00")
    answers_list = []
    
    for answer_data in data.answers:
        # Savolni olish
        question_query = select(ExamQuestion).where(
            ExamQuestion.id == answer_data.question_id
        )
        question_result = await db.execute(question_query)
        question = question_result.scalar_one_or_none()
        
        if not question:
            continue
        
        is_correct = answer_data.user_answer.strip().lower() == question.correct_answer.strip().lower()
        score = question.points if is_correct else Decimal("0.00")
        
        if is_correct:
            correct_count += 1
            total_score += score
        
        answer = ExamAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            user_answer=answer_data.user_answer,
            is_correct=is_correct,
            score=score,
        )
        db.add(answer)
        answers_list.append(answer)
    
    # Attempt'ni yangilash
    attempt.submitted_at = datetime.utcnow()
    attempt.status = "completed"
    attempt.total_score = total_score
    
    # O'tish foizini hisoblash
    total_questions = len(data.answers)
    percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
    
    # O'tgan/o'tmagan
    exam_query = select(Exam).where(Exam.id == exam_id)
    exam_result = await db.execute(exam_query)
    exam = exam_result.scalar_one_or_none()
    
    if exam and exam.passing_score:
        attempt.passed = percentage >= float(exam.passing_score)
    
    await db.commit()
    await db.refresh(attempt)
    
    # Javoblarni qayta o'qish
    answers_query = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt.id)
    answers_result = await db.execute(answers_query)
    answers = answers_result.scalars().all()
    
    return ExamResultResponse(
        attempt=attempt,
        answers=answers,
        total_questions=total_questions,
        correct_answers=correct_count,
        score_percentage=percentage,
    )