"""Content API — CRUD for Video / File lessons (faqat video/file).

Yangi flow: Next.js admin → backend → Telegram API (yopiq kanal) → file_id → DB.
Diskga saqlanmaydi.
"""

import io
import httpx
from fastapi import APIRouter, Depends, Query, File, UploadFile, Form
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.content import ContentItem
from app.schemas.content import ContentItemUpdate, ContentItemResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.config import settings

router = APIRouter(prefix="/content", tags=["content"])

TELEGRAM_API = "https://api.telegram.org/bot"


@router.get("", response_model=List[ContentItemResponse])
def list_content(
    content_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: DBSession = Depends(get_db),
):
    """List all content items with optional filters."""
    query = db.query(ContentItem)
    if content_type:
        query = query.filter(ContentItem.content_type == content_type)
    if is_active is not None:
        query = query.filter(ContentItem.is_active == is_active)
    return query.order_by(ContentItem.id.desc()).all()


@router.post("", response_model=ContentItemResponse)
async def upload_content(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    content_type: str = Form(...),
    cefr_level: Optional[str] = Form(None),
    file: UploadFile = File(...),
    is_active: bool = Form(True),
    db: DBSession = Depends(get_db),
):
    """Faylni to'g'ridan-to'g'ri Telegram API orqali yopiq kanalga yuklaydi,
    file_id ni oladi va DB ga saqlaydi. Diskga yozilmaydi.
    """
    if content_type not in ("video", "file"):
        raise BadRequestException("content_type faqat 'video' yoki 'file' bo'lishi mumkin")

    if not settings.BOT_TOKEN:
        raise BadRequestException("BOT_TOKEN sozlanmagan (.env)")
    if not settings.TELEGRAM_CONTENT_BASE:
        raise BadRequestException("TELEGRAM_CONTENT_BASE sozlanmagan (.env)")

    chat_id = settings.TELEGRAM_CONTENT_BASE
    bot_token = settings.BOT_TOKEN

    content_bytes = await file.read()
    if not content_bytes:
        raise BadRequestException("Fayl bo'sh")

    # Telegram API ga multipart yuborish
    filename = file.filename or "upload"
    file_stream = io.BytesIO(content_bytes)

    telegram_url = f"{TELEGRAM_API}{bot_token}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if content_type == "video":
                tg_resp = await client.post(
                    f"{telegram_url}/sendVideo",
                    data={"chat_id": chat_id, "caption": title},
                    files={"video": (filename, file_stream, file.content_type or "video/mp4")},
                )
            else:
                tg_resp = await client.post(
                    f"{telegram_url}/sendDocument",
                    data={"chat_id": chat_id, "caption": title},
                    files={"document": (filename, file_stream, file.content_type or "application/octet-stream")},
                )
    except Exception as exc:
        raise BadRequestException(f"Telegram API bilan aloqa xatosi: {exc}")

    if tg_resp.status_code != 200:
        raise BadRequestException(
            f"Telegram API xatosi: HTTP {tg_resp.status_code} — {tg_resp.text[:200]}"
        )

    tg_data = tg_resp.json()
    if not tg_data.get("ok"):
        error_msg = tg_data.get('description', 'Noma\'lum xato')
        raise BadRequestException(f"Telegram API xatosi: {error_msg}")


    # file_id ni ajratib olish
    result = tg_data.get("result", {})
    if content_type == "video":
        telegram_file_id = result.get("video", {}).get("file_id")
    else:
        telegram_file_id = result.get("document", {}).get("file_id")

    if not telegram_file_id:
        raise BadRequestException("Telegram javobidan file_id olinmadi")

    # DB ga saqlash
    item = ContentItem(
        title=title,
        description=description,
        content_type=content_type,
        file_path=None,
        telegram_file_id=telegram_file_id,
        is_active=is_active,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.put("/{id}", response_model=ContentItemResponse)
def update_content(
    id: int,
    data: ContentItemUpdate,
    db: DBSession = Depends(get_db),
):
    """Update an existing content item (JSON-only, no file replacement)."""
    item = db.query(ContentItem).filter(ContentItem.id == id).first()
    if not item:
        raise NotFoundException(f"Content item {id} not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{id}", response_model=ContentItemResponse)
async def patch_content(
    id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: DBSession = Depends(get_db),
):
    """Partial update with optional file replacement. If new file uploaded,
    sends to Telegram channel and updates file_id."""
    item = db.query(ContentItem).filter(ContentItem.id == id).first()
    if not item:
        raise NotFoundException(f"Content item {id} not found")

    # Update text fields if provided
    if title is not None:
        item.title = title
    if description is not None:
        item.description = description

    # If new file uploaded, replace via Telegram
    if file and file.filename:
        if not settings.BOT_TOKEN:
            raise BadRequestException("BOT_TOKEN sozlanmagan (.env)")
        if not settings.TELEGRAM_CONTENT_BASE:
            raise BadRequestException("TELEGRAM_CONTENT_BASE sozlanmagan (.env)")

        chat_id = settings.TELEGRAM_CONTENT_BASE
        bot_token = settings.BOT_TOKEN

        content_bytes = await file.read()
        if not content_bytes:
            raise BadRequestException("Fayl bo'sh")

        file_stream = io.BytesIO(content_bytes)
        telegram_url = f"{TELEGRAM_API}{bot_token}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                if item.content_type == "video":
                    tg_resp = await client.post(
                        f"{telegram_url}/sendVideo",
                        data={"chat_id": chat_id, "caption": item.title},
                        files={"video": (file.filename, file_stream, file.content_type or "video/mp4")},
                    )
                else:
                    tg_resp = await client.post(
                        f"{telegram_url}/sendDocument",
                        data={"chat_id": chat_id, "caption": item.title},
                        files={"document": (file.filename, file_stream, file.content_type or "application/octet-stream")},
                    )
        except Exception as exc:
            raise BadRequestException(f"Telegram API bilan aloqa xatosi: {exc}")

        if tg_resp.status_code != 200:
            raise BadRequestException(
                f"Telegram API xatosi: HTTP {tg_resp.status_code} — {tg_resp.text[:200]}"
            )

        tg_data = tg_resp.json()
        if not tg_data.get("ok"):
            raise BadRequestException(
                f"Telegram API xatosi: {tg_data.get('description', 'Noma\'lum xato')}"
            )

        result = tg_data.get("result", {})
        if item.content_type == "video":
            telegram_file_id = result.get("video", {}).get("file_id")
        else:
            telegram_file_id = result.get("document", {}).get("file_id")

        if not telegram_file_id:
            raise BadRequestException("Telegram javobidan file_id olinmadi")

        item.telegram_file_id = telegram_file_id

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id}")
def delete_content(
    id: int,
    db: DBSession = Depends(get_db),
):
    """Delete a content item."""
    item = db.query(ContentItem).filter(ContentItem.id == id).first()
    if not item:
        raise NotFoundException(f"Content item {id} not found")

    db.delete(item)
    db.commit()
    return {"message": f"Content item {id} deleted"}


@router.get("/public", response_model=List[ContentItemResponse])
def list_public_content(
    content_type: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
    db: DBSession = Depends(get_db),
):
    """List active content for public/bot access with pagination."""
    query = db.query(ContentItem).filter(ContentItem.is_active == True)
    if content_type:
        query = query.filter(ContentItem.content_type == content_type)
    return (
        query.order_by(ContentItem.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


@router.post("/{id}/set-telegram-file-id")
def set_telegram_file_id(
    id: int,
    telegram_file_id: str,
    db: DBSession = Depends(get_db),
):
    """Bot calls this: set telegram_file_id after uploading to Telegram."""
    item = db.query(ContentItem).filter(ContentItem.id == id).first()
    if not item:
        raise NotFoundException(f"Content item {id} not found")

    item.telegram_file_id = telegram_file_id
    db.commit()
    db.refresh(item)
    return item
