"""Broadcast handler — bot listens Redis queue and sends messages."""

import asyncio
import json
import logging
from aiogram import Bot
from redis.asyncio import Redis
from bot.config import settings

logger = logging.getLogger(__name__)

BROADCAST_QUEUE = "myestro:broadcast:queue"


async def broadcast_listener(bot: Bot):
    """Listen Redis queue for broadcast jobs and send messages.
    
    Run this as a background task in bot main().
    """
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=False)
    
    logger.info("[BROADCAST LISTENER] Started")
    logger.info(f"[BROADCAST LISTENER] Redis URL: {settings.REDIS_URL}")
    logger.info(f"[BROADCAST LISTENER] Queue name: {BROADCAST_QUEUE}")
    
    MOCK_MODE = False  # Debug: Don't actually send, just log
    
    while True:
        try:
            logger.info("[BROADCAST LISTENER] Waiting for broadcast jobs...")
            # BLPOP — non-blocking async (waits for job)
            result = await redis_client.blpop(BROADCAST_QUEUE, timeout=10)
            
            if not result:
                # Timeout — no jobs
                logger.debug("[BROADCAST LISTENER] Timeout - no jobs")
                continue
            
            _, job_data = result
            job = json.loads(job_data.decode() if isinstance(job_data, bytes) else job_data)
            
            logger.info(f"[BROADCAST] Processing job: {len(job['user_ids'])} users")
            
            message = job.get("message", "")
            media_type = job.get("media_type", "text")
            media_url = job.get("media_url")
            user_ids = job.get("user_ids", [])
            
            # Send to each user
            sent_count = 0
            for user_id in user_ids:
                try:
                    if MOCK_MODE:
                        # Mock: just log
                        logger.info(f"[BROADCAST MOCK] Would send {media_type} to user {user_id}: {message[:50]}...")
                        sent_count += 1
                    else:
                        if media_type == "text":
                            await bot.send_message(
                                chat_id=user_id,
                                text=message,
                                parse_mode="MarkdownV2"
                            )
                        elif media_type == "photo":
                            await bot.send_photo(
                                chat_id=user_id,
                                photo=media_url,
                                caption=message,
                                parse_mode="MarkdownV2"
                            )
                        elif media_type == "video":
                            await bot.send_video(
                                chat_id=user_id,
                                video=media_url,
                                caption=message,
                                parse_mode="MarkdownV2"
                            )
                        elif media_type == "document":
                            await bot.send_document(
                                chat_id=user_id,
                                document=media_url,
                                caption=message,
                                parse_mode="MarkdownV2"
                            )
                        
                        sent_count += 1
                except Exception as e:
                    logger.error(f"[BROADCAST ERROR] User {user_id}: {e}")
                    continue
            
            logger.info(f"[BROADCAST] Sent {sent_count}/{len(user_ids)} messages")
            
        except Exception as e:
            logger.error(f"[BROADCAST LISTENER ERROR] {e}")
            await asyncio.sleep(5)  # Retry after 5s
