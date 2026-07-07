from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    thread_id: int
    user_id: int
    role: str = "user"
    content: str
    content_type: str = "text"
    source: str = "telegram"


class MessageResponse(BaseModel):
    id: int
    thread_id: int
    user_id: int
    role: str
    content: str
    content_type: str
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[int] = None
    cefr_level: Optional[str] = None
    grammar_corrections: Optional[Dict[str, Any]] = None
    vocabulary_suggestions: Optional[Dict[str, Any]] = None
    source: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ThreadCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    cefr_level: str = "A1"


class ThreadResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    cefr_level: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}