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

from bot.handlers import academy, admin, ai_agent, contact, document, errors, menu, photo, profile, referral, register, registration, reminders, start, sticker, video, broadcast

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.config import settings
from bot.handlers import (
    voice,
)
from bot.handlers.broadcast import broadcast_listener
from bot.middlewares.registration import RegistrationMiddleware
from bot.middlewares.ai_guard import AIGuardMiddleware
from bot.middlewares.channel_check import ChannelCheckMiddleware
from bot.utils.ai_client import shutdown_ai_client
from bot.services.ai_service import ai_service
from bot.services.broadcast_worker import BroadcastWorker


logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)





async def main():
    """Initialize and start the bot."""
    logger.info("Starting Myestro Bot...")

    # Redis storage for FSM
    redis_storage = RedisStorage.from_url(settings.REDIS_URL)

    # Bot instance
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Set admin IDs (from env or hardcoded for testing)
    bot.admin_ids = []

    dp = Dispatcher(storage=redis_storage)

    # Debug handler to log incoming text messages
  #  try:
  #     from bot.handlers import debug
   #     dp.include_router(debug.router)
   # except Exception:
    #    logger.warning("Debug router not available")

    dp.include_router(errors.router)       # Error handler first (catch all)
    dp.include_router(start.router)
    dp.include_router(contact.router)      # Phone contact handler
    # AI Agent early so general text messages are handled before reply-keyboard routers
    dp.include_router(register.router)     # New Register/Login flow
    dp.include_router(profile.router)      # Profile + Edit
    dp.include_router(menu.router)         # Reply + callback handlers
    dp.include_router(ai_agent.router)     # AI Agent — voice + advanced text
    dp.include_router(registration.router) # Backend sync
    dp.include_router(voice.router)
    dp.include_router(reminders.router)
    dp.include_router(referral.router)
    dp.include_router(academy.router)
    dp.include_router(admin.router)
    dp.include_router(photo.router)
    dp.include_router(document.router)
    dp.include_router(sticker.router)
    dp.include_router(video.router)
    # fallback.router removed — user requested no catch-all

    # Register middlewares (order matters — channel check first, then AI, then registration)

    # AI Health Check on startup
    logger.info("Running AI health check...")
    try:
        ai_status = await ai_service.health_check()
        if ai_status:
            logger.info("✅ AI health check PASSED — models available")
        else:
            logger.warning("⚠️ AI health check FAILED — check OPENROUTER_API_KEY")
    except Exception as e:
        logger.warning(f"⚠️ AI health check ERROR: {e}")

    logger.info("Bot started polling...")
    broadcast_task = None
    try:
        # Start broadcast listener as background task

        broadcast_task = asyncio.create_task(broadcast_listener(bot))
        
        # Add exception handler to task
        def broadcast_task_exception_handler(task):
            try:
                task.result()
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"[BROADCAST TASK EXCEPTION] {e}", exc_info=True)
        
        broadcast_task.add_done_callback(broadcast_task_exception_handler)
        
        await dp.start_polling(bot)
    finally:
        # Cleanup
        if broadcast_task and not broadcast_task.done():
            broadcast_task.cancel()
        await shutdown_ai_client()
        logger.info("AI client shut down.")


if __name__ == "__main__":
    asyncio.run(main())
