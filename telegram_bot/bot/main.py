import asyncio
import logging
import sys
import os
import httpx

# Add parent directories to path for imports
_app_root = os.path.abspath(os.path.dirname(__file__))
_telegram_bot_root = os.path.abspath(os.path.join(_app_root, ".."))
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)
if _telegram_bot_root not in sys.path:
    sys.path.insert(0, _telegram_bot_root)

from bot.handlers import academy, admin, ai_agent, contact, document, errors, menu, photo, profile, referral, register, reminders, start, sticker, video, broadcast, inbox 
from bot.handlers import test_quiz

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.handlers import voice

from bot.middlewares.ai_guard import AIGuardMiddleware
from bot.middlewares.channel_check import ChannelCheckMiddleware
from bot.middlewares.bot_guard import BotGuardMiddleware
from bot.middlewares.db_session import DbSessionMiddleware
from bot.services.ai_service import ai_service
from bot.services.broadcast_worker import BroadcastWorker
from aiogram.fsm.storage.redis import RedisStorage
from bot.utils.ai_memory_client import AIMemoryClient
from bot.workers.inbox_delivery import inbox_delivery_worker
from redis.asyncio import Redis
from bot.utils.rag_client import rag_client

from bot.utils.text_cache import init_text_cache

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and start the bot."""
    logger.info("Starting Myestro Bot...")

    try:
        logger.info("📚 RAG bilimlar bazasini yuklash boshlandi...")
        chunk_count = rag_client.load_knowledge()
        
        if chunk_count > 0:
            logger.info(f"🔄 {chunk_count} ta chunk uchun embedding hisoblanmoqda...")
            await rag_client.initialize_embeddings()
            logger.info(f"✅ RAG muvaffaqiyatli ishga tushdi! Jami: {chunk_count} ta chunk")
        else:
            logger.warning("⚠️ RAG: knowledge papkasida .md fayllar topilmadi!")
            
    except Exception as e:
        logger.error(f"❌ RAG ishga tushishda jiddiy xato: {e}", exc_info=True)


    # Debug: Check BOT_TOKEN
    if not settings.BOT_TOKEN or settings.BOT_TOKEN.strip() == "":
        logger.error("ERROR: BOT_TOKEN is empty! Set it in Railway environment variables.")
        raise ValueError("BOT_TOKEN environment variable is required")
    
    logger.info(f"OK: BOT_TOKEN loaded (length: {len(settings.BOT_TOKEN)})")

    # ══════════════════════════════════════════════════════════
    # FSM Storage (Redis)
    # ══════════════════════════════════════════════════════════
    redis_storage = RedisStorage.from_url(settings.REDIS_URL + "/1")
    dp = Dispatcher(storage=redis_storage)  # ← BITTA Dispatcher!

    http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_connections=100)
    )

    ai_memory_client = AIMemoryClient(
        backend_url=settings.BACKEND_URL,
        http_client=http_client
    )

    # Store in bot context (for handlers)
    dp["ai_memory_client"] = ai_memory_client
    dp["http_client"] = http_client

    # Bot instance
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Set admin IDs
    bot.admin_ids = []

    # ══════════════════════════════════════════════════════════
    # MIDDLEWARES
    # ══════════════════════════════════════════════════════════
    dp.update.middleware(DbSessionMiddleware())

    # ══════════════════════════════════════════════════════════
    # ROUTERS (tartib muhim!)
    # ══════════════════════════════════════════════════════════
    dp.include_router(errors.router)
    dp.include_router(start.router)
    dp.include_router(contact.router)
    dp.include_router(register.router)
    dp.include_router(profile.router)
    dp.include_router(menu.router)
    dp.include_router(test_quiz.router)
    dp.include_router(inbox.router)
    dp.include_router(ai_agent.router)
    dp.include_router(voice.router)
    dp.include_router(reminders.router)
    dp.include_router(referral.router)
    dp.include_router(academy.router)
    dp.include_router(admin.router)
    dp.include_router(photo.router)
    dp.include_router(document.router)
    dp.include_router(sticker.router)
    dp.include_router(video.router)

    # ══════════════════════════════════════════════════════════
    # MESSAGE MIDDLEWARES
    # ══════════════════════════════════════════════════════════
    dp.message.middleware(BotGuardMiddleware())
    dp.callback_query.middleware(BotGuardMiddleware())
    dp.message.middleware(ChannelCheckMiddleware())
    dp.callback_query.middleware(ChannelCheckMiddleware())
    dp.message.middleware(AIGuardMiddleware())

    # ══════════════════════════════════════════════════════════
    # STARTUP: Text Cache + AI Health Check
    # ══════════════════════════════════════════════════════════
    logger.info("🤖 Bot ishga tushmoqda...")

    # Text cache ni to'ldirish (AWAIT bilan!)
    try:
        count = await init_text_cache()  # ← AWAIT! asyncio.run emas!
        logger.info(f"📝 Text cache yuklandi: {count} matn")
    except Exception as e:
        logger.error(f"❌ Text cache yuklashda xatolik: {e}")

    # AI Health Check
    logger.info("Running AI health check...")
    try:
        ai_status = await ai_service.health_check()
        if ai_status:
            logger.info("OK: AI health check PASSED — models available")
        else:
            logger.warning("WARN: AI health check FAILED — check OPENROUTER_API_KEY")
    except Exception as e:
        logger.warning(f"WARN: AI health check ERROR: {e}")

    logger.info("Bot started polling...")
    
    # ══════════════════════════════════════════════════════════
    # WORKERS
    # ══════════════════════════════════════════════════════════
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=False)
    
    # Start BroadcastWorker
    broadcast_worker = BroadcastWorker(bot, redis_client)
    broadcast_task = asyncio.create_task(broadcast_worker.start())
    
    # Start Inbox delivery worker
    inbox_task = asyncio.create_task(inbox_delivery_worker(bot, redis_client))
    logger.info("🚀 Inbox delivery worker started")
    
    # ══════════════════════════════════════════════════════════
    # POLLING
    # ══════════════════════════════════════════════════════════
    try:
        await dp.start_polling(bot)
    finally:
        broadcast_worker.stop()
        if broadcast_task and not broadcast_task.done():
            broadcast_task.cancel()
        if inbox_task and not inbox_task.done():
            inbox_task.cancel()
        logger.info("Bot shut down.")


if __name__ == "__main__":
    asyncio.run(main())