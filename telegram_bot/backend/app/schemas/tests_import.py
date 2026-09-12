"""
Tests Import Schemas — Quiz import uchun validatsiya
"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, field_validator


class ImportTestOption(BaseModel):
    text: str
    is_correct: bool = False
    order: int = 1


class ImportTestQuestion(BaseModel):
    question_text: str
    question_type: str = "multiple_choice"
    points: int = 1
    order: int = 1
    explanation: Optional[str] = None
    difficulty: str = "medium"
    options: List[ImportTestOption] = []

    @field_validator("question_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"multiple_choice", "single_choice", "multi_choice", "true_false", "short_answer"}
        if v not in allowed:
            raise ValueError(f"question_type '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v

    @field_validator("points")
    @classmethod
    def validate_points(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("points > 0 bo'lishi kerak")
        return v

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed = {"easy", "medium", "hard"}
        if v not in allowed:
            raise ValueError(f"difficulty '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v


class ImportTest(BaseModel):
    title: str
    description: Optional[str] = None
    cefr_level: str
    passing_score: int = 60
    is_active: bool = True
    total_duration: int = 30
    max_score: Optional[int] = None
    questions: List[ImportTestQuestion] = []

    @field_validator("cefr_level")
    @classmethod
    def validate_cefr(cls, v: str) -> str:
        allowed = {"A1", "A2", "B1", "B2", "C1", "C2"}
        if v.upper() not in allowed:
            raise ValueError(f"cefr_level '{v}' noto'g'ri. Ruxsat: {allowed}")
        return v.upper()

    @field_validator("passing_score")
    @classmethod
    def validate_passing_score(cls, v: int) -> int:
        if v < 0 or v > 100:
            raise ValueError("passing_score 0-100 orasida bo'lishi kerak")
        return v


class ImportTestsPayload(BaseModel):
    tests: List[ImportTest]


class TestImportValidationError(BaseModel):
    test_index: Optional[int] = None
    question_index: Optional[int] = None
    location: str
    message: str


class TestImportPreviewResponse(BaseModel):
    valid: bool
    tests_count: int
    total_questions: int
    total_options: int
    errors: List[TestImportValidationError] = []
    warnings: List[str] = []


class TestImportResultResponse(BaseModel):
    success: bool
    tests_created: int = 0
    questions_created: int = 0
    options_created: int = 0
    test_ids: List[int] = []
    errors: List[str] = []