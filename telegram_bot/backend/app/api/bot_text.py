"""Bot text API — CMS for managing bot messages from admin panel."""

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from typing import List, Optional, Dict
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import distinct
from app.database import get_db
from app.models.bot_text import BotText
from app.schemas.bot_text import BotTextCreate, BotTextUpdate, BotTextResponse
from app.core.exceptions import NotFoundException
import httpx
import os

router = APIRouter(prefix="/api/bot-texts", tags=["bot_texts"])

BOT_URL = os.getenv("BOT_API_URL", "http://localhost:8000")


async def notify_bot_cache_refresh():
    """Bot cache ni yangilash uchun webhook yuborish."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(f"{BOT_URL}/internal/refresh-cache")
    except Exception as e:
        # Bot ishlamayotgan bo'lsa, xatolik logga yoziladi
        print(f"[CACHE REFRESH] Bot ga xabar yuborilmadi: {e}")


# ══════════════════════════════════════════════════════════════
# EXISTING CRUD ENDPOINTS (CACHE INVALIDATION QO'SHILDI)
# ══════════════════════════════════════════════════════════════

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
async def create_bot_text(
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
        
        # Cache invalidation
        await notify_bot_cache_refresh()
        return existing

    entry = BotText(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    # Cache invalidation
    await notify_bot_cache_refresh()
    return entry


@router.put("/{id}", response_model=BotTextResponse)
async def update_bot_text(
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
    
    # Cache invalidation
    await notify_bot_cache_refresh()
    return entry


@router.delete("/{id}")
async def delete_bot_text(
    id: int,
    db: DBSession = Depends(get_db),
):
    """Delete a bot text entry."""
    entry = db.query(BotText).filter(BotText.id == id).first()
    if not entry:
        raise NotFoundException(f"Bot text {id} not found")
    db.delete(entry)
    db.commit()
    
    # Cache invalidation
    await notify_bot_cache_refresh()
    return {"message": f"Bot text {id} deleted"}


# ══════════════════════════════════════════════════════════════
# BULK ENDPOINTS (Cache va Admin Panel uchun)
# ══════════════════════════════════════════════════════════════

@router.get("/bulk", response_model=List[BotTextResponse])
def get_all_bot_texts_bulk(
    lang: Optional[str] = Query(None, description="Filter by language (uz, ru, en)"),
    db: DBSession = Depends(get_db),
):
    """
    Get all bot texts in one request (for bot cache initialization).
    
    Use case: Bot ishga tushganda barcha matnlarni Redis cache ga yuklash uchun.
    """
    query = db.query(BotText)
    if lang:
        query = query.filter(BotText.lang == lang)
    return query.all()


@router.post("/bulk-upsert", response_model=List[BotTextResponse])
async def bulk_upsert_bot_texts(
    texts: List[BotTextCreate],
    db: DBSession = Depends(get_db),
):
    """
    Bulk upsert multiple bot texts at once.
    
    Use case: Admin panel bir nechta matnni birdaniga saqlash uchun.
    Agar key+lang kombinatsiyasi mavjud bo'lsa — update, aks holda — create.
    """
    if not texts:
        return []
    
    results = []
    
    try:
        for text_data in texts:
            existing = db.query(BotText).filter(
                BotText.key == text_data.key,
                BotText.lang == text_data.lang,
            ).first()
            
            if existing:
                existing.text = text_data.text
                results.append(existing)
            else:
                entry = BotText(**text_data.model_dump())
                db.add(entry)
                results.append(entry)
        
        db.commit()
        
        # Refresh all entries
        for entry in results:
            db.refresh(entry)
        
        # Cache invalidation
        await notify_bot_cache_refresh()
        
        return results
    
    except Exception as e:
        db.rollback()
        raise


@router.get("/keys", response_model=List[str])
def get_all_bot_text_keys(
    db: DBSession = Depends(get_db),
):
    """
    Get all unique keys from bot_texts table.
    
    Use case: Admin panel filter va qidiruv uchun.
    """
    keys = db.query(distinct(BotText.key)).all()
    return [key[0] for key in keys]


@router.get("/stats")
def get_bot_texts_stats(
    db: DBSession = Depends(get_db),
):
    """
    Get statistics about bot texts (for admin dashboard).
    
    Returns:
        - total: umumiy matnlar soni
        - by_lang: har bir tildagi matnlar soni
        - unique_keys: noyob key'lar soni
    """
    total = db.query(BotText).count()
    
    # Count by language
    uz_count = db.query(BotText).filter(BotText.lang == "uz").count()
    ru_count = db.query(BotText).filter(BotText.lang == "ru").count()
    en_count = db.query(BotText).filter(BotText.lang == "en").count()
    
    # Count unique keys
    unique_keys = db.query(distinct(BotText.key)).count()
    
    return {
        "total": total,
        "by_lang": {
            "uz": uz_count,
            "ru": ru_count,
            "en": en_count,
        },
        "unique_keys": unique_keys,
    }