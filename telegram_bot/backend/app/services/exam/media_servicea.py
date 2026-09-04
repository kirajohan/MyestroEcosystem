"""
Media Service — audio fayllarni saqlash va boshqarish.
Speaking module uchun foydalanuvchi audio'ni qabul qiladi.
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

# ═══════════════════════════════════════════════════════════
# KONFIGURATSIYA
# ═══════════════════════════════════════════════════════════

# Media saqlanadigan asosiy papka (env orqali sozlanadi)
MEDIA_BASE_DIR = Path(os.getenv("MEDIA_DIR", "/app/media"))
EXAM_AUDIO_DIR = MEDIA_BASE_DIR / "exam" / "audio"

# Ruxsat etilgan audio MIME types → extension
ALLOWED_AUDIO_TYPES = {
    "audio/webm": ".webm",     # Chrome, Firefox, Edge
    "audio/mp4": ".mp4",       # Safari fallback
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/x-m4a": ".m4a",
    "audio/aac": ".aac",
}

# Cheklovlar
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024   # 25 MB
MIN_FILE_SIZE_BYTES = 1024               # 1 KB (bo'sh yozuvni rad etish)
MAX_DURATION_SEC = 180                   # 3 daqiqa


class MediaService:
    """Audio fayllarni validation qilish va saqlash."""

    @staticmethod
    def ensure_dirs() -> None:
        """Kerakli papkalarni yaratish (agar yo'q bo'lsa)."""
        EXAM_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_audio(file: UploadFile) -> str:
        """
        Audio fayl MIME type'ini tekshirish.
        Qaytaradi: fayl extension'i (masalan: '.webm')
        Xato bo'lsa: HTTPException 400
        """
        content_type = (file.content_type or "").lower()

        if content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Audio format noto'g'ri: '{content_type}'. "
                    f"Ruxsat etilgan: webm, mp4, mp3, ogg, wav, m4a"
                ),
            )

        return ALLOWED_AUDIO_TYPES[content_type]

    @staticmethod
    async def save_exam_audio(
        file: UploadFile,
        attempt_id: int,
        item_id: int,
    ) -> dict:
        """
        Speaking audio faylni saqlash.

        Args:
            file: Yuklangan audio fayl
            attempt_id: Attempt ID
            item_id: Speaking task item ID

        Returns:
            dict: {
                file_id, file_name, file_path, url,
                size_bytes, mime_type, extension
            }

        Raises:
            HTTPException: Validation xatosi
        """
        MediaService.ensure_dirs()

        # 1. MIME type tekshirish
        ext = MediaService.validate_audio(file)

        # 2. Fayl nomini generatsiya qilish
        file_id = uuid.uuid4().hex
        file_name = f"exam_audio_{attempt_id}_{item_id}_{file_id}{ext}"
        file_path = EXAM_AUDIO_DIR / file_name

        # 3. Faylni o'qish va hajmini tekshirish
        content = await file.read()
        size_bytes = len(content)

        if size_bytes > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fayl hajmi {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB dan oshmasligi kerak",
            )

        if size_bytes < MIN_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio fayl juda kichik. Qayta yozib ko'ring.",
            )

        # 4. Faylni diskga yozish
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Faylni saqlashda xato: {str(e)}",
            )

        # 5. URL (static serving orqali ochiladi)
        url = f"/media/exam/audio/{file_name}"

        return {
            "file_id": file_id,
            "file_name": file_name,
            "file_path": str(file_path),
            "url": url,
            "size_bytes": size_bytes,
            "mime_type": file.content_type,
            "extension": ext,
        }

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Faylni o'chirish (xato bo'lsa False)."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
        except OSError:
            pass
        return False