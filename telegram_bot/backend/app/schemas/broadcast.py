from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class MediaType(str, Enum):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"

class TargetAudience(BaseModel):
    all: bool = False
    active: bool = False  # oxirgi 7 kunda faol
    roles: Optional[List[str]] = None  # ["student", "teacher"]
    cefr_levels: Optional[List[str]] = None  # ["A1", "B2"]

class BroadcastRequest(BaseModel):
    text: Optional[str] = Field(None, max_length=4096)
    media_type: MediaType = MediaType.TEXT
    media_url: Optional[str] = None
    target: TargetAudience
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Yangi kurs boshlandi!",
                "media_type": "photo",
                "media_url": "https://example.com/image.jpg",
                "target": {
                    "all": True,
                    "roles": ["student"]
                }
            }
        }