"""Admin message schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdminMessageBase(BaseModel):
    user_id: Optional[int] = None
    user_telegram_id: Optional[int] = None
    user_name: Optional[str] = None
    content_type: str = "text"
    text: Optional[str] = None
    file_id: Optional[str] = None


class AdminMessageCreate(AdminMessageBase):
    pass


class AdminMessageReply(BaseModel):
    reply: str


class AdminMessageResponse(AdminMessageBase):
    id: int
    is_read: bool = False
    is_replied: bool = False
    admin_reply: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
