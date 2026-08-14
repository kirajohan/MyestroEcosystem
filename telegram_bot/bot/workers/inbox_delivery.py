"""Inbox delivery worker — Send admin replies to users via Telegram."""

import asyncio
import json
import logging
from aiogram import Bot

logger = logging.getLogger(__name__)


async def inbox_delivery_worker(bot: Bot, redis):
    """Worker that listens to Redis queue and sends admin replies to users."""
    logger.info("📨 Inbox delivery worker started")
    
    while True:
        try:
            # Wait for new message in queue
            _, raw = await redis.brpop("inbox:admin_replies")
            
            data = json.loads(raw)
            
            telegram_id = data["telegram_id"]
            text = data["text"]
            inbox_message_id = data["inbox_message_id"]
            admin_name = data.get("admin_name", "Admin")
            
            # Send to user
            await bot.send_message(
                chat_id=telegram_id,
                text=f"📩 <b>Admin javobi:</b>\n\n{text}",
                parse_mode="HTML"
            )
            
            logger.info(f"✅ Admin reply delivered to user {telegram_id} (message {inbox_message_id})")
            
        except Exception as e:
            logger.error(f"❌ Inbox delivery error: {e}")
            await asyncio.sleep(2)  # Wait before retry