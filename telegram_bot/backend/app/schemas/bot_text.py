"""Bot text (CMS) schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BotTextBase(BaseModel):
    key: str
    lang: str = "uz"
    text: str


class BotTextCreate(BotTextBase):
    pass


class BotTextUpdate(BaseModel):
    text: str


class BotTextResponse(BotTextBase):
    id: int
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
