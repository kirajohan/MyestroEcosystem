from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schemas.knowledge import KnowledgeCategoryResponse, KnowledgeDocResponse
from app.models.knowledge import KnowledgeCategory, KnowledgeDoc

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/categories", response_model=List[KnowledgeCategoryResponse])
def get_categories(
    db: DBSession = Depends(get_db),
):
    categories = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.is_active == True
    ).order_by(KnowledgeCategory.order_index).all()
    return [KnowledgeCategoryResponse.model_validate(c) for c in categories]


@router.get("/docs", response_model=List[KnowledgeDocResponse])
def get_docs(
    category_id: int = None,
    cefr_level: str = None,
    db: DBSession = Depends(get_db),
):
    query = db.query(KnowledgeDoc).filter(KnowledgeDoc.is_active == True)
    if category_id:
        query = query.filter(KnowledgeDoc.category_id == category_id)
    if cefr_level:
        query = query.filter(KnowledgeDoc.cefr_level == cefr_level)
    docs = query.all()
    return [KnowledgeDocResponse.model_validate(d) for d in docs]
