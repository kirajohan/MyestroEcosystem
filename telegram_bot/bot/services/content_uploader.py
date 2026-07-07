"""Content uploader — bot uploads files to Telegram and saves file_id."""

import asyncio
import logging
import httpx
from aiogram import Bot
from bot.config import settings

logger = logging.getLogger(__name__)

CONTENT_API = f"{settings.API_BASE_URL or 'http://backend:8000'}/content"


async def upload_content_to_telegram(bot: Bot, content_id: int, file_path: str, content_type: str):
    """Upload file to Telegram and save file_id.
    
    content_type: 'video' or 'file'
    """
    try:
        logger.info(f"[CONTENT UPLOADER] Uploading {content_type} {content_id}: {file_path}")
        
        # Upload to Telegram
        if content_type == "video":
            try:
                with open(file_path, 'rb') as f:
                    msg = await bot.send_video(
                        chat_id=settings.TELEGRAM_CONTENT_BASE or settings.BOT_TOKEN.split(':')[0],
                        video=f
                    )
                telegram_file_id = msg.video.file_id
            except Exception as e:
                logger.error(f"[CONTENT UPLOADER] Video upload error: {e}")
                return
        
        elif content_type == "file":
            try:
                with open(file_path, 'rb') as f:
                    msg = await bot.send_document(
                        chat_id=settings.TELEGRAM_CONTENT_BASE or settings.BOT_TOKEN.split(':')[0],
                        document=f
                    )
                telegram_file_id = msg.document.file_id
            except Exception as e:
                logger.error(f"[CONTENT UPLOADER] Document upload error: {e}")
                return
        else:
            logger.error(f"[CONTENT UPLOADER] Invalid content_type: {content_type}")
            return
        
        # Save file_id to backend
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{CONTENT_API}/{content_id}/set-telegram-file-id",
                    json={"telegram_file_id": telegram_file_id},
                    headers={"Authorization": f"Bearer {settings.BOT_TOKEN}"}
                )
                if resp.status_code == 200:
                    logger.info(f"[CONTENT UPLOADER] Saved telegram_file_id for {content_type} {content_id}")
                else:
                    logger.error(f"[CONTENT UPLOADER] Backend error: {resp.status_code}")
        except Exception as e:
            logger.error(f"[CONTENT UPLOADER] Backend error: {e}")
            
    except Exception as e:
        logger.error(f"[CONTENT UPLOADER] Error: {e}")
