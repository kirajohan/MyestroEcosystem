"""Bot text API — CMS for managing bot messages from admin panel."""

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.bot_text import BotText
from app.schemas.bot_text import BotTextCreate, BotTextUpdate, BotTextResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/bot-texts", tags=["bot_texts"])


@router.get("", response_model=List[BotTextResponse])
def list_bot_texts(
    key: Optional[str] = Query(None),
    lang: Optional[str] = Query(None),
    db: DBSession = Depends(get_db),
):
    """List bot texts with optional filters."""
    query = db.query(BotText)
    if key:
        query = query.filter(BotText.key == key)
    if lang:
        query = query.filter(BotText.lang == lang)
    return query.all()


@router.post("", response_model=BotTextResponse)
def create_bot_text(
    data: BotTextCreate,
    db: DBSession = Depends(get_db),
):
    """Create a new bot text entry."""
    existing = db.query(BotText).filter(
        BotText.key == data.key,
        BotText.lang == data.lang,
    ).first()
    if existing:
        existing.text = data.text
        db.commit()
        db.refresh(existing)
        return existing

    entry = BotText(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{id}", response_model=BotTextResponse)
def update_bot_text(
    id: int,
    data: BotTextUpdate,
    db: DBSession = Depends(get_db),
):
    """Update a bot text entry."""
    entry = db.query(BotText).filter(BotText.id == id).first()
    if not entry:
        raise NotFoundException(f"Bot text {id} not found")
    entry.text = data.text
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{id}")
def delete_bot_text(
    id: int,
    db: DBSession = Depends(get_db),
):
    """Delete a bot text entry."""
    entry = db.query(BotText).filter(BotText.id == id).first()
    if not entry:
        raise NotFoundException(f"Bot text {id} not found")
    db.delete(entry)
    db.commit()
    return {"message": f"Bot text {id} deleted"}
