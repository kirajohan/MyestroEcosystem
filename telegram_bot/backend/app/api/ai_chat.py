# /backend/app/api/ai_chat.py

from fastapi import APIRouter, Depends, Query
from aiogram.types import Message as TgMessage
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import httpx

from app.config import settings
from app.database import get_async_db
from app.models.conversation import ConversationThread
from app.core.exceptions import NotFoundException

TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

router = APIRouter(prefix="/conversations", tags=["AI Chat"])

@router.get("/threads")
async def get_user_threads(
    user_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Foydalanuvchining active thread'larini olish
    (THREADED MODE'da topic'lar)
    """
    threads = await db.execute(
        select(ConversationThread)
        .where(ConversationThread.user_id == user_id)
        .where(ConversationThread.is_active == True)
        .order_by(desc(ConversationThread.last_message_at))
        .limit(10)
    )
    return [
        {
            "id": t.id,
            "telegram_topic_id": t.telegram_topic_id,
            "title": t.topic_title,
            "cefr_level": t.cefr_level,
            "last_message_at": t.last_message_at
        }
        for t in threads.scalars().all()
    ]

@router.post("/threads")
async def create_thread(
    user_id: int,
    telegram_topic_id: int,  # Bot'dan keladi
    topic_title: str,
    cefr_level: str = "A1",
    db: AsyncSession = Depends(get_async_db)
):
    """
    Yangi topic thread yaratish
    Telegram topic ID automatik track qilamiz
    """
    thread = ConversationThread(
        user_id=user_id,
        telegram_topic_id=telegram_topic_id,
        topic_title=topic_title,
        cefr_level=cefr_level
    )
    db.add(thread)
    await db.commit()
    return thread

@router.get("/threads/{topic_id}/history")
async def get_topic_message_history(
    topic_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    THREADED MODE KEY ENDPOINT

    Telegram topic'dagi barcha xabarlarni olish
    (Telegram API orqali history retrieve)

    NOTE: BotService integration hali to'liq implement qilinmagan.
    Hozircha faqat database'dan metadata qaytariladi.
    """

    # 1. Database'dan thread metadata'ni ol
    thread = await db.execute(
        select(ConversationThread)
        .where(ConversationThread.telegram_topic_id == topic_id)
    )
    thread_obj = thread.scalar_one_or_none()

    if not thread_obj:
        raise NotFoundException("Thread not found")

    # 2. Telegram API orqali topic message history'ni ol
    # NOTE: BotService hali implement qilinmagan - bo'sh list qaytaramiz
    messages_history = []

    # 3. Format: AI uchun readable format
    chat_history = []
    for msg in messages_history:
        if msg.text:
            chat_history.append({
                "role": "user",
                "content": msg.text,
                "timestamp": msg.date
            })

    return {
        "topic_id": topic_id,
        "title": thread_obj.topic_title,
        "cefr_level": thread_obj.cefr_level,
        "messages": chat_history
    }

@router.post("/threads/{topic_id}/send-message")
async def send_message_to_topic(
    topic_id: int,
    content: str,
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """
    THREADED MODE: AI Javob beradigan endpoint

    1. Topic message history'ni ol (Telegram API)
    2. AI bilan suhbat (full context bilan)
    3. AI javobini topic'ga yubor

    NOTE: BotService va AIService integration hali to'liq implement qilinmagan.
    """

    # 1. Telegram topic message history'ni ol
    # NOTE: BotService hali implement qilinmagan - bo'sh list qaytaramiz
    messages = []

    # 2. Chat history yaratish (AI uchun)
    chat_history = []
    for msg in messages:
        if msg.text:
            chat_history.append({
                "role": "user",
                "content": msg.text
            })

    # 3. Foydalanuvchining yangi xabarini append
    chat_history.append({
        "role": "user",
        "content": content
    })

    # 4. AI bilan suhbat (full context)
    thread = await db.execute(
        select(ConversationThread)
        .where(ConversationThread.telegram_topic_id == topic_id)
    )
    thread_obj = thread.scalar_one_or_none()

    if not thread_obj:
        raise NotFoundException("Thread not found")

    # NOTE: AIService hali implement qilinmagan
    ai_response = {"text": "AI service not yet implemented"}

    # 5. Database'da last_message_at update
    thread_obj.last_message_at = datetime.utcnow()
    await db.commit()

    return {
        "status": "sent",
        "ai_response": ai_response["text"]
    }