from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cefr_level: str = "A1"
    status: str = "draft"
    total_duration: int = 0
    reading_duration: int = 0
    listening_duration: int = 0
    speaking_duration: int = 0
    writing_duration: int = 0
    ownership_type: str = "owned"
    passing_score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    is_sample: bool = False
    attempt_limit: int = 1


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
    is_active: bool = True
    attempt_limit: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


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