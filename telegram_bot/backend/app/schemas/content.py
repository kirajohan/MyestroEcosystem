"""Content schemas for Video / File / Text lessons."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ContentItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: str  # "video" yoki "file"
    file_path: Optional[str] = None
    telegram_file_id: Optional[str] = None
    is_active: bool = True


class ContentItemCreate(ContentItemBase):
    pass


class ContentItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None
    file_path: Optional[str] = None
    telegram_file_id: Optional[str] = None
    is_active: Optional[bool] = None


class ContentItemResponse(ContentItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
