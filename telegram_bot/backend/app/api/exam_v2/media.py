"""
Maestro Exam — Media upload endpoints.

POST /api/v2/exam/admin/media/upload → audio/image fayl yuklash
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_admin_user
from app.database import get_async_db
from app.models.user import User

router = APIRouter()

# Media fayllar saqlanadigan papka
MEDIA_DIR = Path("/app/media/exam")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Ruxsat etilgan MIME types
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/ogg",
    "audio/webm",
    "audio/mp4",
    "audio/x-m4a",
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Media fayl yuklash (audio/image)",
)
async def upload_media(
    file: UploadFile = File(...),
    file_type: str = "audio",  # "audio" yoki "image"
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Audio yoki image faylni yuklaydi.
    Qaytaradi: fayl URL (relative path)
    """

    # 1. MIME type tekshirish
    content_type = file.content_type or ""
    
    if file_type == "audio":
        if content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Audio format noto'g'ri: {content_type}. Ruxsat: mp3, wav, ogg, webm"
            )
    elif file_type == "image":
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Image format noto'g'ri: {content_type}. Ruxsat: jpg, png, webp, gif"
            )
    else:
        raise HTTPException(status_code=400, detail="file_type: 'audio' yoki 'image' bo'lishi kerak")

    # 2. Fayl hajmini tekshirish
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Fayl hajmi {MAX_FILE_SIZE_MB}MB dan oshmasligi kerak"
        )

    # 3. Fayl nomini generatsiya qilish
    ext = Path(file.filename or "file").suffix or ".mp3"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    
    # Subdirectory: audio yoki image
    subdir = MEDIA_DIR / file_type
    subdir.mkdir(exist_ok=True)
    
    file_path = subdir / unique_name

    # 4. Faylni saqlash
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 5. URL qaytarish (relative path)
    relative_url = f"/media/exam/{file_type}/{unique_name}"

    return {
        "url": relative_url,
        "file_name": file.filename,
        "size_bytes": len(file_content),
        "content_type": content_type,
    }