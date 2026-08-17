from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# ══════════════════════════════════════════════════════════════
# EXAM (TEST) SCHEMAS
# ══════════════════════════════════════════════════════════════

class ExamCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cefr_level: str = Field(default="A1", pattern="^(A0|A1|A2|B1|B2|C1|C2)$")
    status: str = Field(default="draft", pattern="^(draft|published|archived)$")
    total_duration: int = Field(default=0, ge=0)
    reading_duration: int = Field(default=0, ge=0)
    listening_duration: int = Field(default=0, ge=0)
    speaking_duration: int = Field(default=0, ge=0)
    writing_duration: int = Field(default=0, ge=0)
    ownership_type: str = Field(default="owned")
    passing_score: Optional[Decimal] = Field(default=None, ge=0, le=100)
    max_score: Optional[Decimal] = Field(default=None, ge=0)
    is_sample: bool = False
    attempt_limit: int = Field(default=1, ge=1)
    is_published: bool = False


class ExamUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    cefr_level: Optional[str] = Field(default=None, pattern="^(A0|A1|A2|B1|B2|C1|C2)$")
    status: Optional[str] = Field(default=None, pattern="^(draft|published|archived)$")
    total_duration: Optional[int] = Field(default=None, ge=0)
    reading_duration: Optional[int] = Field(default=None, ge=0)
    listening_duration: Optional[int] = Field(default=None, ge=0)
    speaking_duration: Optional[int] = Field(default=None, ge=0)
    writing_duration: Optional[int] = Field(default=None, ge=0)
    ownership_type: Optional[str] = None
    passing_score: Optional[Decimal] = Field(default=None, ge=0, le=100)
    max_score: Optional[Decimal] = Field(default=None, ge=0)
    is_sample: Optional[bool] = None
    attempt_limit: Optional[int] = Field(default=None, ge=1)
    is_published: Optional[bool] = None
    channel_post_id: Optional[int] = None
    published_at: Optional[datetime] = None


class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    cefr_level: str
    status: str
    total_duration: int
    reading_duration: int
    listening_duration: int
    speaking_duration: int
    writing_duration: int
    ownership_type: str
    partner_name: Optional[str] = None
    pdf_url: Optional[str] = None
    mp3_url: Optional[str] = None
    passing_score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    version: int
    is_sample: bool
    attempt_limit: int
    is_published: bool
    channel_post_id: Optional[int] = None
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════
# SECTION SCHEMAS
# ══════════════════════════════════════════════════════════════

class ExamSectionCreate(BaseModel):
    section_type: str = Field(default="quiz")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    duration_minutes: int = Field(default=0, ge=0)
    order_index: int = Field(default=0, ge=0)
    instructions: Optional[str] = None
    total_questions: int = Field(default=0, ge=0)
    max_score: Optional[Decimal] = Field(default=None, ge=0)
    passing_score: Optional[Decimal] = Field(default=None, ge=0, le=100)


class ExamSectionResponse(BaseModel):
    id: int
    exam_id: int
    section_type: str
    title: str
    description: Optional[str] = None
    duration_minutes: int
    order_index: int
    instructions: Optional[str] = None
    total_questions: int
    max_score: Optional[Decimal] = None
    passing_score: Optional[Decimal] = None

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════
# QUESTION SCHEMAS
# ══════════════════════════════════════════════════════════════

class ExamQuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1)
    question_type: str = Field(default="multiple_choice")
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    points: Decimal = Field(default=Decimal("1.00"), ge=0)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    order_index: int = Field(default=0, ge=0)


class ExamQuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(default=None, min_length=1)
    question_type: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[str] = Field(default=None, min_length=1)
    explanation: Optional[str] = None
    points: Optional[Decimal] = Field(default=None, ge=0)
    difficulty: Optional[str] = Field(default=None, pattern="^(easy|medium|hard)$")
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    order_index: Optional[int] = Field(default=None, ge=0)


class ExamQuestionResponse(BaseModel):
    id: int
    section_id: int
    question_number: int
    question_type: str
    question_text: str
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: Decimal
    difficulty: str
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    order_index: int

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════
# ATTEMPT & ANSWER SCHEMAS
# ══════════════════════════════════════════════════════════════

class ExamAttemptCreate(BaseModel):
    exam_id: int


class ExamAttemptResponse(BaseModel):
    id: int
    exam_id: int
    user_id: int
    attempt_number: int
    status: str
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    reading_score: Optional[Decimal] = None
    listening_score: Optional[Decimal] = None
    speaking_score: Optional[Decimal] = None
    writing_score: Optional[Decimal] = None
    total_score: Optional[Decimal] = None
    cefr_result: Optional[str] = None
    passed: Optional[bool] = None
    confidence_score: Optional[Decimal] = None

    model_config = {"from_attributes": True}


class ExamAnswerCreate(BaseModel):
    question_id: int
    user_answer: str


class ExamAnswerResponse(BaseModel):
    id: int
    attempt_id: int
    question_id: int
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[Decimal] = None
    ai_feedback: Optional[str] = None
    answered_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExamSubmitRequest(BaseModel):
    attempt_id: int
    answers: List[ExamAnswerCreate]


class ExamResultResponse(BaseModel):
    attempt: ExamAttemptResponse
    answers: List[ExamAnswerResponse]
    total_questions: int
    correct_answers: int
    score_percentage: float