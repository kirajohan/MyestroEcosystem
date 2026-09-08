# telegram_bot/backend/api/tests.py
"""
Tests API — Telegram Quiz Poll uchun testlar va savollar.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_async_db
from app.models.tests import Test, TestQuestion, TestAttempt

router = APIRouter(prefix="/tests", tags=["tests"])

# ══════════════════════════════════════════════════════════════
# SCHEMAS (Pydantic)
# ══════════════════════════════════════════════════════════════

class TestOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cefr_level: str
    passing_score: int
    is_active: bool
    total_duration: int = 30
    max_score: Optional[int] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cefr_level: str
    passing_score: int = 60
    is_active: bool = True
    total_duration: int = 30


class TestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cefr_level: Optional[str] = None
    passing_score: Optional[int] = None
    is_active: Optional[bool] = None
    total_duration: Optional[int] = None


class QuestionOut(BaseModel):
    id: int
    question_text: str
    question_type: str = "multiple_choice"
    options: list
    correct_answer: str  # Bu endi index bo'ladi: "0", "1", "2", "3"
    explanation: Optional[str]
    points: int = 1
    difficulty: str = "medium"
    order_index: int
    
    class Config:
        from_attributes = True
        

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    options: list  # ["option1", "option2", "option3", "option4"]
    correct_option_index: int  # 0, 1, 2, 3 dan biri
    explanation: Optional[str] = None
    points: int = 1
    difficulty: str = "medium"


class TestWithQuestionsOut(BaseModel):
    id: int
    title: str
    passing_score: int
    questions: List[QuestionOut]


class TestAttemptCreate(BaseModel):
    user_id: int
    test_id: int
    score: int
    total_questions: int
    percentage: int
    passed: bool


class TestAttemptOut(BaseModel):
    id: int
    user_id: int
    test_id: int
    score: int
    total_questions: int
    percentage: int
    passed: bool
    
    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════

# ── GET ALL TESTS ──
@router.get("", response_model=List[TestOut])
async def get_public_tests_all(
    level: Optional[str] = Query(None, description="CEFR daraja (A1, A2, B1, B2, C1, C2)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(True, description="Faqat faol testlar"),
    db: AsyncSession = Depends(get_async_db)
):
    """Faol testlar ro'yxatini qaytarish."""
    try:
        query = select(Test)
        
        if active_only:
            query = query.where(Test.is_active == True)
        
        if level:
            query = query.where(Test.cefr_level == level.upper())
        
        query = query.order_by(Test.created_at.desc()).offset(offset).limit(limit)
        
        result = await db.execute(query)
        tests = result.scalars().all()
        
        return tests
    except Exception as e:
        print(f"Error in get_public_tests_all: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── CREATE TEST ──
@router.post("", response_model=TestOut, status_code=201)
async def create_test(
    test_data: TestCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Yangi test yaratish."""
    try:
        new_test = Test(
            title=test_data.title,
            description=test_data.description,
            cefr_level=test_data.cefr_level.upper(),
            passing_score=test_data.passing_score,
            is_active=test_data.is_active,
            total_duration=test_data.total_duration,
            status="active"
        )
        
        db.add(new_test)
        await db.commit()
        await db.refresh(new_test)
        
        return new_test
    except Exception as e:
        await db.rollback()
        print(f"Error in create_test: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── GET SINGLE TEST ──
@router.get("/{test_id}", response_model=TestOut)
async def get_test(
    test_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Bitta testni olish."""
    try:
        result = await db.execute(select(Test).where(Test.id == test_id))
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Test topilmadi")
        
        return test
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_test: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── UPDATE TEST ──
@router.put("/{test_id}", response_model=TestOut)
async def update_test(
    test_id: int,
    test_data: TestUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Testni yangilash."""
    try:
        result = await db.execute(select(Test).where(Test.id == test_id))
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Test topilmadi")
        
        # Faqat berilgan fieldlarni yangilash
        if test_data.title is not None:
            test.title = test_data.title
        if test_data.description is not None:
            test.description = test_data.description
        if test_data.cefr_level is not None:
            test.cefr_level = test_data.cefr_level.upper()
        if test_data.passing_score is not None:
            test.passing_score = test_data.passing_score
        if test_data.is_active is not None:
            test.is_active = test_data.is_active
        if test_data.total_duration is not None:
            test.total_duration = test_data.total_duration
        
        test.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(test)
        
        return test
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in update_test: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── DELETE TEST ──
@router.delete("/{test_id}", status_code=204)
async def delete_test(
    test_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Testni o'chirish."""
    try:
        result = await db.execute(select(Test).where(Test.id == test_id))
        test = result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Test topilmadi")
        
        # Savollarni o'chirish
        await db.execute(
            delete(TestQuestion).where(TestQuestion.test_id == test_id)
        )
        await db.delete(test)
        await db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in delete_test: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── GET TEST QUESTIONS ──
@router.get("/{test_id}/questions", response_model=TestWithQuestionsOut)
async def get_test_questions(
    test_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Test savollarini qaytarish."""
    try:
        # Testni topish
        test_result = await db.execute(select(Test).where(Test.id == test_id))
        test = test_result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Test topilmadi")
        
        # Savollarni olish (tartib bo'yicha)
        questions_result = await db.execute(
            select(TestQuestion)
            .where(TestQuestion.test_id == test_id)
            .order_by(TestQuestion.order_index)
        )
        questions = questions_result.scalars().all()
        
        return TestWithQuestionsOut(
            id=test.id,
            title=test.title,
            passing_score=test.passing_score,
            questions=[QuestionOut.model_validate(q) for q in questions]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_test_questions: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── CREATE QUESTION ──
@router.post("/{test_id}/questions", response_model=QuestionOut, status_code=201)
async def create_question(
    test_id: int,
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Testga savol qo'shish."""
    try:
        # Testni tekshirish
        test_result = await db.execute(select(Test).where(Test.id == test_id))
        test = test_result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Test topilmadi")
        
        # Oxirgi order_index ni topish
        last_question = await db.execute(
            select(TestQuestion)
            .where(TestQuestion.test_id == test_id)
            .order_by(TestQuestion.order_index.desc())
        )
        last_q = last_question.scalars().first()
        next_order_index = (last_q.order_index + 1) if last_q else 1
        
        new_question = TestQuestion(
            test_id=test_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            options=question_data.options,
            correct_answer=str(question_data.correct_option_index),
            explanation=question_data.explanation,
            points=question_data.points,
            difficulty=question_data.difficulty,
            order_index=next_order_index
        )
        
        db.add(new_question)
        await db.commit()
        await db.refresh(new_question)
        
        return new_question
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in create_question: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ── CREATE TEST ATTEMPT ──
@router.post("/attempts", response_model=TestAttemptOut, status_code=201)
async def create_test_attempt(
    attempt: TestAttemptCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Test natijasini saqlash."""
    try:
        # Test mavjudligini tekshirish
        test_result = await db.execute(select(Test).where(Test.id == attempt.test_id))
        test = test_result.scalar_one_or_none()
        
        if not test:
            raise HTTPException(status_code=404, detail="Test topilmadi")
        
        # Yangi attempt yaratish
        new_attempt = TestAttempt(
            user_id=attempt.user_id,
            test_id=attempt.test_id,
            score=attempt.score,
            total_questions=attempt.total_questions,
            percentage=attempt.percentage,
            passed=attempt.passed
        )
        
        db.add(new_attempt)
        await db.commit()
        await db.refresh(new_attempt)
        
        return new_attempt
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error in create_test_attempt: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ... (mavjud importlar ostiga qo'shing)
import json
from app.services.ai_service import ask_ai  # Sizning loyihangizdagi AI client import yo'li

# ══════════════════════════════════════════════════════════════
# AI GENERATION SCHEMAS
# ══════════════════════════════════════════════════════════════

class AITestGenerateRequest(BaseModel):
    title: str
    cefr_level: str
    num_questions: int = 5
    topic: Optional[str] = "General English"


class GeneratedQuestion(BaseModel):
    question_text: str
    options: list[str]
    correct_option_index: int
    explanation: Optional[str] = ""
    difficulty: str = "medium"


# ══════════════════════════════════════════════════════════════
# AI GENERATE ENDPOINT
# ══════════════════════════════════════════════════════════════

@router.post("/ai-generate", response_model=TestOut, status_code=201)
async def ai_generate_and_create_test(
    req: AITestGenerateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """AI yordamida test va uning savollarini avtomatik yaratish."""
    try:
        # 1. AI uchun qat'iy prompt
        system_prompt = """Sen professional ingliz tili o'qituvchisisan. Faqat va faqat JSON formatida javob qaytar. Boshqa hech qanday matn yozma.
        JSON quyidagi formatda bo'lishi shart:
        [
          {
            "question_text": "Savol matni",
            "options": ["Variant A", "Variant B", "Variant C", "Variant D"],
            "correct_option_index": 0,
            "explanation": "Qisqa tushuntirish",
            "difficulty": "medium"
          }
        ]"""
        
        user_prompt = f"""{req.cefr_level} darajasi uchun '{req.topic}' mavzusida {req.num_questions} ta multiple-choice test savoli yarat. 
        To'g'ri javob indeksi 0 dan 3 gacha bo'lishi kerak."""

        # 2. AI dan javob olish
        ai_response = await ask_ai(prompt=user_prompt, system_prompt=system_prompt, model="openai/gpt-4o-mini")
        
        # 3. JSON ni tozalash va parse qilish
        clean_json = ai_response.strip().replace("```json", "").replace("```", "").strip()
        questions_data = json.loads(clean_json)
        
        if not isinstance(questions_data, list) or len(questions_data) == 0:
            raise HTTPException(status_code=500, detail="AI noto'g'ri format qaytardi")

        # 4. Testni bazaga saqlash
        new_test = Test(
            title=req.title,
            description=f"AI tomonidan yaratilgan: {req.topic} ({req.cefr_level})",
            cefr_level=req.cefr_level.upper(),
            passing_score=60,
            is_active=True,
            total_duration=req.num_questions * 2,  # Har bir savolga 2 daqiqa
            status="active"
        )
        db.add(new_test)
        await db.flush()  # ID olish uchun

        # 5. Savollarni bazaga saqlash
        for idx, q_data in enumerate(questions_data):
            new_question = TestQuestion(
                test_id=new_test.id,
                question_text=q_data.get("question_text", ""),
                question_type="multiple_choice",
                options=q_data.get("options", []),
                correct_answer=str(q_data.get("correct_option_index", 0)),
                explanation=q_data.get("explanation", ""),
                points=1,
                difficulty=q_data.get("difficulty", "medium"),
                order_index=idx + 1
            )
            db.add(new_question)

        await db.commit()
        await db.refresh(new_test)
        
        return new_test

    except json.JSONDecodeError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="AI JSON formatida javob bermadi. Qayta urinib ko'ring.")
    except Exception as e:
        await db.rollback()
        print(f"AI Generate Error: {e}")
        raise HTTPException(status_code=500, detail=f"Xatolik: {str(e)}")