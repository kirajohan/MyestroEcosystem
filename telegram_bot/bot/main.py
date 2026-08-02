import asyncio
import logging
import sys
import os

# Add parent directories to path for imports
_app_root = os.path.abspath(os.path.dirname(__file__))
_telegram_bot_root = os.path.abspath(os.path.join(_app_root, ".."))
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)
if _telegram_bot_root not in sys.path:
    sys.path.insert(0, _telegram_bot_root)

from bot.handlers import academy, admin, ai_agent, ai_chat, contact, document, errors, menu, photo, profile, referral, register, registration, reminders, start, sticker, video, inbox, lessons, test

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.handlers import (
    voice,
)
from bot.middlewares.ai_guard import AIGuardMiddleware
from bot.middlewares.channel_check import ChannelCheckMiddleware
from bot.services.ai_service import ai_service
from bot.services.broadcast_worker import BroadcastWorker


logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main():
    """Initialize and start the bot."""
    logger.info("Starting Myestro Bot...")

    # Debug: Check BOT_TOKEN
    if not settings.BOT_TOKEN or settings.BOT_TOKEN.strip() == "":
        logger.error("ERROR: BOT_TOKEN is empty! Set it in Railway environment variables.")
        raise ValueError("BOT_TOKEN environment variable is required")
    
    logger.info(f"OK: BOT_TOKEN loaded (length: {len(settings.BOT_TOKEN)})")

    # FSM Storage (Memory — no Redis)
    storage = MemoryStorage()

    # Bot instance
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Set admin IDs (from env or hardcoded for testing)
    bot.admin_ids = []

    dp = Dispatcher(storage=storage)

    dp.include_router(errors.router)
    dp.include_router(start.router)
    dp.include_router(contact.router)
    dp.include_router(register.router)
    dp.include_router(profile.router)
    dp.include_router(menu.router)
    dp.include_router(lessons.router)
    dp.include_router(test.router)
    dp.include_router(ai_chat.router)
    dp.include_router(ai_agent.router)
    dp.include_router(registration.router)
    dp.include_router(inbox.router)
    dp.include_router(voice.router)
    dp.include_router(reminders.router)
    dp.include_router(referral.router)
    dp.include_router(academy.router)
    dp.include_router(admin.router)
    dp.include_router(photo.router)
    dp.include_router(document.router)
    dp.include_router(sticker.router)
    dp.include_router(video.router)

    # Register middlewares
    dp.message.middleware(ChannelCheckMiddleware())
    dp.callback_query.middleware(ChannelCheckMiddleware())
    dp.message.middleware(AIGuardMiddleware())

    # AI Health Check on startup
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
    # Start BroadcastWorker (Redis queue consumer)
    # ✅ decode_responses=True — string ma'lumotlar uchun (progress tracking, user data)
    # Binary ma'lumotlar (media upload) uchun worker ichida alohida ulanish yaratiladi
    from redis.asyncio import Redis
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    broadcast_worker = BroadcastWorker(bot, redis_client)
    broadcast_task = asyncio.create_task(broadcast_worker.start())
    
    try:
        await dp.start_polling(bot)
    finally:
        await broadcast_worker.stop()
        if broadcast_task and not broadcast_task.done():
            try:
                await asyncio.wait_for(broadcast_task, timeout=10)
            except asyncio.TimeoutError:
                broadcast_task.cancel()
                try:
                    await broadcast_task
                except asyncio.CancelledError:
                    pass
        await redis_client.aclose()
        logger.info("AI client shut down.")


if __name__ == "__main__":
    asyncio.run(main())