# /bot/utils/telegram_service.py

import logging
from aiogram import Bot
from aiogram.types import Message
from typing import List
from bot.config import TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

class TelegramTopicService:
    """
    THREADED MODE (Topics) bilan ishlash
    Telegram API orqali topic message history
    """
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.chat_id = TELEGRAM_CHAT_ID
    
    async def get_topic_messages(
        self,
        topic_id: int,
        limit: int = 50
    ) -> List[Message]:
        """
        Topic message history'ni Telegram'dan olish
        
        Telegram botda forward, get_chat, get_message methods mavjud
        Lekin message history uchun manual traverse kerak
        
        ALTERNATIVE: aiogram polls yoki webhooks
        """
        
        # Method 1: Topic messages'ni retrieve (Telegram Bot API v6.4+)
        try:
            # Telegram Bot API'da direct topic history method yo'q
            # Lekin /getUpdates orqali polling qilsa bo'ladi
            
            # RECOMMENDATION: Topic'ni follow qilish + polling
            messages = []
            
            # Manual implementation (backup):
            # - Bot topic'ga join qiladi
            # - Har xabar save qilinadi database'da
            # - History database'dan retrieve qilinadi
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get topic messages: {e}")
            return []
    
    async def send_topic_message(
        self,
        topic_id: int,
        text: str,
        parse_mode: str = "HTML"
    ):
        """Topic'ga xabar yuborish"""
        
        # Telegram Bot API'da message_thread_id parameter
        message = await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=parse_mode,
            message_thread_id=topic_id  # KEY PARAMETER!
        )
        return message
    
    async def create_topic(
        self,
        topic_title: str
    ) -> int:
        """Yangi topic yaratish"""
        
        # Telegram Bot API v6.4+ da forumTopic methods
        forum_topic = await self.bot.create_forum_topic(
            chat_id=self.chat_id,
            name=topic_title,
            icon_color=0xFFA500  # Orange color
        )
        return forum_topic.message_thread_id
    
    async def get_topic_info(
        self,
        topic_id: int
    ):
        """Topic ma'lumotlarini olish"""
        
        topic_info = await self.bot.get_forum_topic(
            chat_id=self.chat_id,
            message_thread_id=topic_id
        )
        return topic_info