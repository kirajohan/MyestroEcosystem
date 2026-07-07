import asyncio
import json
import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramBadRequest
from aiogram.types import FSInputFile
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class BroadcastWorker:
    def __init__(self, bot: Bot, redis: Redis):
        self.bot = bot
        self.redis = redis
        self.queue_name = "myestro:broadcast:queue"
        self.running = False
    
    async def start(self):
        """Background task sifatida ishga tushirish"""
        self.running = True
        logger.info("🎧 Broadcast worker started...")
        
        while self.running:
            try:
                # BRPOP — blocking pop, 5 sekund kutadi
                raw_job = await self.redis.brpop(self.queue_name, timeout=5)
                
                if not raw_job:
                    continue
                
                # raw_job = (queue_name, job_json)
                job_data = raw_job[1]
                job = json.loads(job_data)
                
                await self._process_job(job)
                
            except Exception as e:
                logger.error(f"Worker critical error: {e}", exc_info=True)
                await asyncio.sleep(5)
    
    async def stop(self):
        """Worker'ni to'xtatish"""
        self.running = False
        logger.info("🛑 Broadcast worker stopped")
    
    async def _process_job(self, job: dict):
        """Bitta job'ni qayta ishlash"""
        broadcast_id = job["id"]
        user_ids = job["user_ids"]
        content = job["content"]
        progress_key = job["progress_key"]
        
        logger.info(f"📤 Processing broadcast {broadcast_id}, batch {job.get('batch_number', 0)}, {len(user_ids)} users")
        
        # Status'ni "sending" ga o'zgartirish
        await self.redis.hset(progress_key, "status", "sending")
        
        # Media file_id cache (optimizatsiya)
        media_file_id = await self._get_or_upload_media(content)
        
        for user_id in user_ids:
            try:
                await self._send_message(user_id, content, media_file_id)
                
                # Progress'ni yangilash
                await self.redis.hincrby(progress_key, "sent", 1)
                
                # Rate limit himoyasi — sekundiga ~25 ta xabar
                await asyncio.sleep(0.04)
                
            except TelegramRetryAfter as e:
                logger.warning(f"FloodWait {e.retry_after}s for user {user_id}")
                await asyncio.sleep(e.retry_after)
                # Qayta urinib ko'rish
                try:
                    await self._send_message(user_id, content, media_file_id)
                    await self.redis.hincrby(progress_key, "sent", 1)
                except Exception:
                    await self.redis.hincrby(progress_key, "failed", 1)
                    
            except TelegramForbiddenError:
                logger.info(f"User {user_id} blocked the bot")
                await self.redis.hincrby(progress_key, "failed", 1)
                await self.redis.sadd(f"broadcast:{broadcast_id}:failed_users", user_id)
                
            except TelegramBadRequest as e:
                logger.warning(f"Bad request for user {user_id}: {e}")
                await self.redis.hincrby(progress_key, "failed", 1)
                
            except Exception as e:
                logger.error(f"Error sending to {user_id}: {e}", exc_info=True)
                await self.redis.hincrby(progress_key, "failed", 1)
        
        # Batch tugadi, agar barcha batch'lar tugagan bo'lsa, status'ni "completed" qilish
        # (Bu yerda oddiy yechim — har bir batch o'zini o'zi tugatadi)
        logger.info(f"✅ Batch {job.get('batch_number', 0)} completed for broadcast {broadcast_id}")
    
    async def _get_or_upload_media(self, content: dict) -> Optional[str]:
        """Media file_id ni olish yoki yuklash"""
        media_type = content.get("media_type")
        media_url = content.get("media_url")
        
        if not media_url or media_type == "text":
            return None
        
        # Agar media_url allaqachon file_id bo'lsa (Telegram formatida)
        if media_url.startswith("AgAC") or media_url.startswith("BAAD"):
            return media_url
        
        # Aks holda, faylni yuklash kerak
        # TODO: File ID cache qo'shish (Redis'da saqlash)
        try:
            if media_type == "photo":
                # URL'dan rasm yuklash
                msg = await self.bot.send_photo(
                    chat_id=self.bot.id,  # O'ziga yuborish
                    photo=media_url,
                    caption="Temp upload for file_id"
                )
                file_id = msg.photo[-1].file_id
                await msg.delete()
                return file_id
                
            elif media_type == "video":
                msg = await self.bot.send_video(
                    chat_id=self.bot.id,
                    video=media_url,
                    caption="Temp upload for file_id"
                )
                file_id = msg.video.file_id
                await msg.delete()
                return file_id
                
            elif media_type == "document":
                msg = await self.bot.send_document(
                    chat_id=self.bot.id,
                    document=media_url
                )
                file_id = msg.document.file_id
                await msg.delete()
                return file_id
                
        except Exception as e:
            logger.error(f"Failed to upload media: {e}")
            return None
    
    async def _send_message(self, user_id: int, content: dict, media_file_id: Optional[str]):
        """Send message to user with HTML parse mode support."""
        text = content.get("content", content.get("text", ""))  # Support both "content" and "text"
        message_type = content.get("message_type", content.get("media_type", "text"))
        
        if message_type == "text" or not media_file_id:
            # Text only
            await self.bot.send_message(
                user_id, 
                text,
                parse_mode="HTML"  # Support HTML formatting
            )
            
        elif message_type == "photo":
            await self.bot.send_photo(
                user_id, 
                photo=media_file_id, 
                caption=text,
                parse_mode="HTML"
            )
            
        elif message_type == "video":
            await self.bot.send_video(
                user_id, 
                video=media_file_id, 
                caption=text,
                parse_mode="HTML"
            )
            
        elif message_type == "document":
            await self.bot.send_document(
                user_id, 
                document=media_file_id, 
                caption=text,
                parse_mode="HTML"
            )