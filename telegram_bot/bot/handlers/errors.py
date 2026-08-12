import logging
import asyncio
import traceback
from aiogram import Router, types
from aiogram.types import ErrorEvent
from aiogram.fsm.context import FSMContext
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)

router = Router()


@router.errors()
async def global_error_handler(event: ErrorEvent, state: FSMContext = None):
    """Global error handler — catch all unhandled exceptions."""
    exception = event.exception
    update = event.update

    # Log the error
    logger.error(
        "Unhandled error: %s\nTraceback: %s",
        str(exception),
        traceback.format_exc(),
    )

    user_id = None
    chat_id = None
    lang = "uz"

    if update.message:
        user_id = update.message.from_user.id
        chat_id = update.message.chat.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
        chat_id = update.callback_query.message.chat.id
        lang = update.callback_query.from_user.language_code or "uz"

    # Try to notify user
    if chat_id:
        try:
            # Determine error type for user-friendly message
            error_message = get_text("error", lang)

            if isinstance(exception, asyncio.TimeoutError):
                error_message = get_text("error_timeout", lang)
            elif "Redis" in str(type(exception).__name__) or "redis" in str(exception).lower():
                error_message = get_text("error_redis", lang)
            elif "Connection" in str(type(exception).__name__):
                error_message = get_text("error_redis", lang)

            # Try to send via bot instance
            bot = event.update.message.bot if event.update.message else None
            if not bot and event.update.callback_query:
                bot = event.update.callback_query.message.bot

            if bot:
                await bot.send_message(
                    chat_id=chat_id,
                    text=error_message,
                )
        except Exception:
            logger.exception("Failed to send error message to user")

    # In production: log to error_logs table via Backend API
    logger.info(
        "Error handled: user_id=%s, chat_id=%s, error=%s",
        user_id, chat_id, str(exception),
    )

    # Return True to mark error as handled
    return True

