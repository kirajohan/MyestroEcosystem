"""
Exam Import Schemas — JSON import uchun validatsiya
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, field_validator


class ImportOption(BaseModel):
    text: str
    is_correct: bool = False
    order: int = 1


class ImportItem(BaseModel):
    block_code: str
    item_type: str
    title: str
    question_text: Optional[str] = None
    instruction: Optional[str] = None
    passage_text: Optional[str] = None
    audio_url: Optional[str] = None
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    preparation_time_sec: Optional[int] = None
    answer_time_sec: Optional[int] = None
    max_score: float = 1.0
    order: int = 1
    options: List[ImportOption] = []

    @field_validator("item_type")
    @classmethod
    def validate_item_type(cls, v: str) -> str:
        allowed = {
            "listening_question", "reading_question",
            "writing_task", "speaking_task"
        }
        if v not in allowed:
            raise ValueError(f"item_type '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v

    @field_validator("max_score")
    @classmethod
    def validate_max_score(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("max_score > 0 bo'lishi kerak")
        return v


class ImportBlock(BaseModel):
    block_code: str
    block_type: str
    title: str
    instructions: Optional[str] = None
    passage_text: Optional[str] = None
    audio_url: Optional[str] = None
    order: int = 1
    time_limit_sec: int = 600

    @field_validator("block_type")
    @classmethod
    def validate_block_type(cls, v: str) -> str:
        allowed = {"listening", "reading", "writing", "speaking"}
        if v not in allowed:
            raise ValueError(f"block_type '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v


class ImportExam(BaseModel):
    code: str
    title: str
    exam_type: str
    cefr_level: str
    description: Optional[str] = None
    time_limit_sec: int = 3600
    is_published: bool = False
    blocks: List[ImportBlock] = []
    items: List[ImportItem] = []

    @field_validator("exam_type")
    @classmethod
    def validate_exam_type(cls, v: str) -> str:
        allowed = {"full", "listening", "reading", "writing", "speaking"}
        if v not in allowed:
            raise ValueError(f"exam_type '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v

    @field_validator("cefr_level")
    @classmethod
    def validate_cefr(cls, v: str) -> str:
        allowed = {"A1", "A2", "B1", "B2", "C1", "C2"}
        if v.upper() not in allowed:
            raise ValueError(f"cefr_level '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v.upper()


class ImportValidationError(BaseModel):
    location: str       # masalan: "items[3].block_code"
    message: str


class ImportPreviewResponse(BaseModel):
    """Validatsiya natijasi — admin ko'rib chiqishi uchun"""
    valid: bool
    exam_title: str
    exam_type: str
    cefr_level: str
    blocks_count: int
    items_count: int
    options_count: int
    errors: List[ImportValidationError] = []
    warnings: List[str] = []
    parsed_data: Optional[ImportExam] = None  # faqat valid bo'lsa


class ImportConfirmRequest(BaseModel):
    """Tasdiqlash so'rovi"""
    data: ImportExam


class ImportResultResponse(BaseModel):
    """Import natijasi"""
    success: bool
    exam_id: Optional[int] = None
    blocks_created: int = 0
    items_created: int = 0
    options_created: int = 0
    errors: List[str] = []