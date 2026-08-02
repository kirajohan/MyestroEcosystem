"""Content uploader — bot uploads files to Telegram and saves file_id."""

import asyncio
import logging
import httpx
from aiogram import Bot
from bot.config import settings

logger = logging.getLogger(__name__)

CONTENT_API = f"{settings.API_BASE_URL or 'http://backend:8002'}/content"

# Archive channel — used for content uploads to Telegram storage
# Priority: ARCHIVE_CHAT_ID → TELEGRAM_CONTENT_BASE
ARCHIVE_CHAT_ID = getattr(settings, "ARCHIVE_CHAT_ID", None) or getattr(settings, "TELEGRAM_CONTENT_BASE", None)


async def upload_content_to_telegram(bot: Bot, content_id: int, file_path: str, content_type: str):
    """Upload file to Telegram and save file_id.
    
    content_type: 'video' or 'file'
    
    Returns:
        tuple[bool, Optional[str]]: (success, telegram_file_id or error_message)
    """
    if not ARCHIVE_CHAT_ID:
        error_msg = "ARCHIVE_CHAT_ID or TELEGRAM_CONTENT_BASE not configured"
        logger.error(f"[CONTENT UPLOADER] {error_msg}")
        return False, error_msg
    
    try:
        logger.info(f"[CONTENT UPLOADER] Uploading {content_type} {content_id}: {file_path}")
        
        # Upload to Telegram
        telegram_file_id = None
        
        if content_type == "video":
            try:
                with open(file_path, 'rb') as f:
                    msg = await bot.send_video(
                        chat_id=ARCHIVE_CHAT_ID,
                        video=f
                    )
                telegram_file_id = msg.video.file_id
                logger.info(f"[CONTENT UPLOADER] Video uploaded successfully: {telegram_file_id}")
            except Exception as e:
                error_msg = f"Video upload error: {e}"
                logger.error(f"[CONTENT UPLOADER] {error_msg}")
                return False, error_msg
        
        elif content_type == "file":
            try:
                with open(file_path, 'rb') as f:
                    msg = await bot.send_document(
                        chat_id=ARCHIVE_CHAT_ID,
                        document=f
                    )
                telegram_file_id = msg.document.file_id
                logger.info(f"[CONTENT UPLOADER] Document uploaded successfully: {telegram_file_id}")
            except Exception as e:
                error_msg = f"Document upload error: {e}"
                logger.error(f"[CONTENT UPLOADER] {error_msg}")
                return False, error_msg
        else:
            error_msg = f"Invalid content_type: {content_type}"
            logger.error(f"[CONTENT UPLOADER] {error_msg}")
            return False, error_msg
        
        # Save file_id to backend
        if telegram_file_id:
            try:
                # Use API key from settings if available, otherwise skip auth header
                headers = {}
                if hasattr(settings, 'API_KEY') and settings.API_KEY:
                    headers["Authorization"] = f"Bearer {settings.API_KEY}"
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"{CONTENT_API}/{content_id}/set-telegram-file-id",
                        json={"telegram_file_id": telegram_file_id},
                        headers=headers
                    )
                    if resp.status_code == 200:
                        logger.info(f"[CONTENT UPLOADER] Saved telegram_file_id for {content_type} {content_id}")
                        return True, telegram_file_id
                    else:
                        error_msg = f"Backend error: HTTP {resp.status_code} - {resp.text[:200]}"
                        logger.error(f"[CONTENT UPLOADER] {error_msg}")
                        return False, error_msg
            except Exception as e:
                error_msg = f"Backend error: {e}"
                logger.error(f"[CONTENT UPLOADER] {error_msg}")
                return False, error_msg
            
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"[CONTENT UPLOADER] {error_msg}", exc_info=True)
        return False, error_msg
