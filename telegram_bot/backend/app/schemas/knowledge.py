from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class KnowledgeCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    order_index: int
    is_active: bool

    model_config = {"from_attributes": True}


class KnowledgeDocResponse(BaseModel):
    id: int
    category_id: Optional[int] = None
    title: str
    slug: str
    file_path: str
    cefr_level: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    is_active: bool

    model_config = {"from_attributes": True}