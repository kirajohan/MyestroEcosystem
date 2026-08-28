"""
Maestro Exam — Pydantic Schemas
API uchun kirish/chiqish ma'lumotlarini validatsiya qilish.

XAVFSIZLIK PRINCIPI:
- ...Read    → admin uchun to'liq ma'lumot (answer_key, is_correct bor)
- ...Public  → foydalanuvchi uchun xavfsiz (to'g'ri javoblar YASHIRILGAN)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.exam_enums import (
    AIAnswerStatus,
    AIJobStatus,
    AIJobType,
    AttemptStatus,
    BlockAttemptStatus,
    CEFRLevel,
    ExamType,
    ItemType,
)


# =====================================================
# BASE — ORM dan o'qish uchun umumiy konfiguratsiya
# =====================================================

# =====================================================
# 1.2 PHONE + PASSWORD AUTH
# =====================================================


class PhoneLoginRequest(BaseModel):
    """Telefon + parol orqali login (Maestro Exam web)."""
    phone: str = Field(..., description="Telefon raqam, masalan: +998901234567")
    password: str = Field(..., min_length=4, description="Parol")


class ORMModel(BaseModel):
    """SQLAlchemy model -> Pydantic o'tkazish uchun baza."""
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# 1. TELEGRAM AUTH
# =====================================================
class TelegramLoginRequest(BaseModel):
    """Telegram Login Widget dan keladigan ma'lumotlar."""
    id: int = Field(..., description="Telegram user ID (telegram_id)")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int = Field(..., description="Unix timestamp")
    hash: str = Field(..., description="Telegram tomonidan berilgan hash")


class UserBrief(BaseModel):
    """Login javobida qaytariladigan qisqa foydalanuvchi ma'lumoti.

    Eslatma: users jadvalida `full_name` va `telegram_username` bor,
    `first_name` emas. Shuning uchun shu maydonlardan foydalanamiz.
    """
    id: int
    full_name: Optional[str] = None
    telegram_id: Optional[int] = None
    telegram_username: Optional[str] = None
    cefr_level: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "student"


class TelegramLoginResponse(BaseModel):
    """Telegram login muvaffaqiyatli bo'lganda qaytariladigan javob."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserBrief


# =====================================================
# 2. EXAMS
# =====================================================
class ExamBase(BaseModel):
    """Imtihon yaratish/yangilash uchun umumiy maydonlar."""
    code: str = Field(..., min_length=2, max_length=100, description="Unikal kod, masalan: full_exam_b1")
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    exam_type: ExamType
    cefr_level: Optional[CEFRLevel] = None
    time_limit_sec: int = Field(default=0, ge=0, description="Umumiy vaqt (soniya)")
    is_published: bool = False
    scoring_config: Optional[dict[str, Any]] = Field(
        default=None,
        description="Baholash sozlamalari, masalan: {'listening_weight': 25, ...}"
    )


class ExamCreate(ExamBase):
    """Admin imtihon yaratishda ishlatadi."""
    pass


class ExamUpdate(BaseModel):
    """Admin imtihonni yangilashda ishlatadi (barcha maydonlar ixtiyoriy)."""
    code: Optional[str] = Field(None, min_length=2, max_length=100)
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    exam_type: Optional[ExamType] = None
    cefr_level: Optional[CEFRLevel] = None
    time_limit_sec: Optional[int] = Field(None, ge=0)
    is_published: Optional[bool] = None
    scoring_config: Optional[dict[str, Any]] = None


class ExamRead(ExamBase, ORMModel):
    """Admin uchun to'liq imtihon ma'lumoti."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ExamListItem(BaseModel):
    """Foydalanuvchiga imtihonlar ro'yxatida ko'rsatiladigan qisqa ma'lumot."""
    id: int
    code: str
    title: str
    description: Optional[str] = None
    exam_type: ExamType
    cefr_level: Optional[CEFRLevel] = None
    time_limit_sec: int


class ExamListResponse(BaseModel):
    """Imtihonlar ro'yxati javobi."""
    items: list[ExamListItem]
    total: int


# =====================================================
# 3. EXAM BLOCKS
# =====================================================
class ExamBlockBase(BaseModel):
    """Imtihon bloki uchun umumiy maydonlar."""
    exam_id: int
    block_type: ExamType = Field(..., description="listening/reading/writing/speaking")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = Field(None, description="Foydalanuvchiga ko'rsatiladigan yo'riqnoma")
    order: int = Field(default=0, ge=0)
    time_limit_sec: int = Field(default=0, ge=0)
    config: Optional[dict[str, Any]] = Field(
        default=None,
        description="Qo'shimcha sozlamalar, masalan: {'max_listens': 2}"
    )


class ExamBlockCreate(ExamBlockBase):
    """Admin blok yaratishda ishlatadi."""
    pass


class ExamBlockUpdate(BaseModel):
    """Admin blokni yangilashda ishlatadi."""
    block_type: Optional[ExamType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    time_limit_sec: Optional[int] = Field(None, ge=0)
    config: Optional[dict[str, Any]] = None


class ExamBlockRead(ExamBlockBase, ORMModel):
    """Admin uchun to'liq blok ma'lumoti."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# =====================================================
# 4. EXAM OPTIONS (javob variantlari)
# =====================================================
class ExamOptionBase(BaseModel):
    """Javob varianti uchun umumiy maydonlar."""
    item_id: int
    text: str = Field(..., min_length=1)
    is_correct: bool = False
    order: int = Field(default=0, ge=0)


class ExamOptionCreate(ExamOptionBase):
    """Admin variant qo'shishda ishlatadi."""
    pass


class ExamOptionUpdate(BaseModel):
    """Admin variantni yangilashda ishlatadi."""
    text: Optional[str] = None
    is_correct: Optional[bool] = None
    order: Optional[int] = Field(None, ge=0)


class ExamOptionRead(ExamOptionBase, ORMModel):
    """ADMIN uchun — is_correct KO'RINADI."""
    id: int
    created_at: datetime


class ExamOptionPublic(BaseModel):
    """FOYDALANUVCHI uchun — is_correct YASHIRILGAN! ⚠️"""
    id: int
    text: str
    order: int


# =====================================================
# 5. EXAM ITEMS (savollar / topshiriqlar)
# =====================================================
class ExamItemBase(BaseModel):
    """Savol/topshiriq uchun umumiy maydonlar."""
    block_id: int
    item_type: ItemType
    title: Optional[str] = None
    instruction: Optional[str] = None
    question_text: Optional[str] = None
    passage_text: Optional[str] = Field(None, description="Reading uchun matn")
    audio_url: Optional[str] = None
    audio_duration_sec: Optional[int] = Field(None, ge=0)
    transcript_text: Optional[str] = Field(None, description="Listening/Speaking etalon transkript")
    min_words: Optional[int] = Field(None, ge=0, description="Writing uchun")
    max_words: Optional[int] = Field(None, ge=0, description="Writing uchun")
    preparation_time_sec: Optional[int] = Field(None, ge=0, description="Speaking uchun")
    answer_time_sec: Optional[int] = Field(None, ge=0, description="Speaking uchun")
    max_score: float = Field(default=1.0, ge=0)
    order: int = Field(default=0, ge=0)
    config: Optional[dict[str, Any]] = None
    answer_key: Optional[dict[str, Any]] = Field(
        None,
        description="Avtomatik tekshirish uchun to'g'ri javoblar"
    )
    rubric_id: Optional[int] = None


class ExamItemCreate(ExamItemBase):
    """Admin savol yaratishda ishlatadi."""
    pass


class ExamItemUpdate(BaseModel):
    """Admin savolni yangilashda ishlatadi."""
    item_type: Optional[ItemType] = None
    title: Optional[str] = None
    instruction: Optional[str] = None
    question_text: Optional[str] = None
    passage_text: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration_sec: Optional[int] = None
    transcript_text: Optional[str] = None
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    preparation_time_sec: Optional[int] = None
    answer_time_sec: Optional[int] = None
    max_score: Optional[float] = Field(None, ge=0)
    order: Optional[int] = None
    config: Optional[dict[str, Any]] = None
    answer_key: Optional[dict[str, Any]] = None
    rubric_id: Optional[int] = None


class ExamItemRead(ExamItemBase, ORMModel):
    """ADMIN uchun — answer_key KO'RINADI."""
    id: int
    created_at: datetime
    options: list[ExamOptionRead] = []


class ExamItemPublic(BaseModel):
    """FOYDALANUVCHI uchun — answer_key YASHIRILGAN! ⚠️"""
    id: int
    item_type: ItemType
    title: Optional[str] = None
    instruction: Optional[str] = None
    question_text: Optional[str] = None
    passage_text: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration_sec: Optional[int] = None
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    preparation_time_sec: Optional[int] = None
    answer_time_sec: Optional[int] = None
    max_score: float
    order: int
    options: list[ExamOptionPublic] = []


# =====================================================
# 6. EXAM RUBRICS (AI baholash shablonlari)
# =====================================================
class ExamRubricBase(BaseModel):
    """AI baholash rubrikasi uchun umumiy maydonlar."""
    code: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=255)
    skill_type: ExamType = Field(..., description="writing yoki speaking")
    system_prompt: str
    user_prompt_template: str
    scoring_schema: dict[str, Any] = Field(default_factory=dict)
    cefr_mapping: Optional[dict[str, Any]] = None
    is_active: bool = True


class ExamRubricCreate(ExamRubricBase):
    """Admin rubrika yaratishda ishlatadi."""
    pass


class ExamRubricUpdate(BaseModel):
    """Admin rubrikani yangilashda ishlatadi."""
    code: Optional[str] = None
    name: Optional[str] = None
    skill_type: Optional[ExamType] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    scoring_schema: Optional[dict[str, Any]] = None
    cefr_mapping: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class ExamRubricRead(ExamRubricBase, ORMModel):
    """Admin uchun to'liq rubrika ma'lumoti."""
    id: int
    created_at: datetime


# =====================================================
# 7. EXAM ATTEMPTS (urinishlar)
# =====================================================
class ExamAttemptCreate(BaseModel):
    """Foydalanuvchi imtihonni boshlashda yuboradi."""
    exam_id: int


class AttemptBlockRead(BaseModel):
    """Urinish ichidagi blok holati."""
    id: int
    block_id: int
    block_type: Optional[ExamType] = None
    title: Optional[str] = None
    status: BlockAttemptStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None


class ExamAttemptRead(ORMModel):
    """Urinishning to'liq holati."""
    id: int
    user_id: int
    exam_id: int
    status: AttemptStatus
    started_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_score: Optional[float] = None
    cefr_estimate: Optional[str] = None
    created_at: datetime


class ExamAttemptStartResponse(BaseModel):
    """Imtihon boshlanganda qaytariladigan javob."""
    attempt_id: int
    exam_id: int
    status: AttemptStatus
    started_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    blocks: list[AttemptBlockRead] = []


# =====================================================
# 8. EXAM ANSWERS (javoblar)
# =====================================================
class AnswerSubmit(BaseModel):
    """Foydalanuvchi javob yuborishda ishlatadi.

    - Listening/Reading: selected_options
    - Writing: text_answer
    """
    item_id: int
    selected_options: Optional[list[int]] = Field(
        None,
        description="Tanlangan variant ID lari, masalan: [3] yoki [1, 4]"
    )
    text_answer: Optional[str] = Field(
        None,
        description="Writing uchun matnli javob"
    )


class AnswerRead(ORMModel):
    """Javobning to'liq holati (natijalarda ko'rsatiladi)."""
    id: int
    attempt_id: int
    item_id: int
    selected_options: Optional[list[int]] = None
    text_answer: Optional[str] = None
    audio_url: Optional[str] = None
    transcript_text: Optional[str] = None
    auto_score: Optional[float] = None
    ai_score: Optional[float] = None
    final_score: Optional[float] = None
    ai_status: Optional[AIAnswerStatus] = None
    feedback: Optional[dict[str, Any]] = None
    created_at: datetime


# =====================================================
# 9. EXAM AI JOBS
# =====================================================
class AIJobRead(ORMModel):
    """AI vazifasining holati."""
    id: int
    attempt_id: int
    answer_id: Optional[int] = None
    job_type: AIJobType
    status: AIJobStatus
    provider: Optional[str] = None
    error_message: Optional[str] = None
    attempts_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# =====================================================
# 10. RESULTS (natijalar)
# =====================================================
class BlockResult(BaseModel):
    """Blok bo'yicha natija."""
    block_id: int
    block_type: ExamType
    title: Optional[str] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    status: BlockAttemptStatus


class ExamResult(BaseModel):
    """Imtihonning to'liq natijasi."""
    attempt_id: int
    exam_id: int
    exam_title: str
    status: AttemptStatus
    total_score: Optional[float] = None
    cefr_estimate: Optional[str] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    blocks: list[BlockResult] = []
    answers: list[AnswerRead] = []


# =====================================================
# 11. AI STATUS
# =====================================================
class AIStatusResponse(BaseModel):
    """Imtihon uchun AI baholash holati (polling uchun)."""
    attempt_id: int
    status: AttemptStatus
    ai_jobs: list[AIJobRead] = []
    pending_count: int = 0
    processing_count: int = 0
    completed_count: int = 0
    error_count: int = 0