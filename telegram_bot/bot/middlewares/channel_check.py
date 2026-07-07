"""Channel subscription middleware — check if user is subscribed to required channel.

If user is not subscribed, block all handlers and show subscription prompt.
Skips check for:
- /start command
- Channel join callback
- Admin users
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject, ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from bot.config import settings
from bot.utils.i18n import get_text
from bot.keyboards.inline import channel_subscribe_kb
from bot.config import settings

logger = logging.getLogger(__name__)


class ChannelCheckMiddleware(BaseMiddleware):
    """Check if user is subscribed to the required Telegram channel."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Skip if no channel configured
        if not settings.CHANNEL_ID:
            logger.debug("[CHANNEL CHECK] No channel configured, skipping")
            return await handler(event, data)

        # Skip for ChatMemberUpdated (channel join events)
        if isinstance(event, ChatMemberUpdated):
            logger.debug("[CHANNEL CHECK] ChatMemberUpdated event, skipping")
            return await handler(event, data)

        # Get user_id
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            # Skip /start command
            if event.text and event.text.startswith("/start"):
                logger.debug(f"[CHANNEL CHECK] /start command, user {user_id}, skipping")
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            # Skip channel join callback
            if event.data and event.data.startswith("channel_joined"):
                logger.debug(f"[CHANNEL CHECK] channel_joined callback, user {user_id}, skipping")
                return await handler(event, data)

        if not user_id:
            return await handler(event, data)

        # Check subscription status
        bot = data.get("bot")
        if not bot:
            return await handler(event, data)

        try:
            logger.debug(f"[CHANNEL CHECK] Checking subscription for user {user_id} in channel {settings.CHANNEL_ID}")
            member = await bot.get_chat_member(settings.CHANNEL_ID, user_id)
            logger.debug(f"[CHANNEL CHECK] User {user_id} member status: {member.status}")
            
            if member.status in {"member", "administrator", "creator"}:
                logger.debug(f"[CHANNEL CHECK] User {user_id} is subscribed, allowing")
                return await handler(event, data)
            else:
                logger.debug(f"[CHANNEL CHECK] User {user_id} status '{member.status}' not allowed")
                
        except Exception as e:
            logger.error(f"[CHANNEL CHECK] Error checking membership for user {user_id}: {e}")
            # On error, allow through (graceful degradation) — don't block users due to bot permission issues
            return await handler(event, data)

        # User is not subscribed — check trial counter and allow limited trials
        state: FSMContext = data.get("state")
        lang = "uz"
        trial = settings.AI_TRIAL_LIMIT
        if state:
            user_data = await state.get_data()
            lang = user_data.get("lang", "uz")
            trial = user_data.get("ai_trial_count", settings.AI_TRIAL_LIMIT)

        if trial > 0:
            # decrement trial and allow through
            await state.update_data(ai_trial_count=trial - 1)
            logger.info(f"[CHANNEL CHECK] User {user_id} not subscribed but has trial={trial}, allowing and decrementing")
            # Optionally notify user about remaining trials on first/last usage
            try:
                if isinstance(event, Message):
                    await event.answer(f"✅ Sizda {trial - 1} ta bepul AI javob qoldi. Obuna bo'lish uchun: {settings.CHANNEL_URL}")
            except Exception:
                pass
            return await handler(event, data)

        logger.info(f"[CHANNEL CHECK] User {user_id} is NOT subscribed and no trials left, blocking access")

        if isinstance(event, Message):
            await event.answer(
                get_text("channel.required", lang, channel_url=settings.CHANNEL_URL),
                reply_markup=channel_subscribe_kb(lang, settings.CHANNEL_URL),
            )
        elif isinstance(event, CallbackQuery):
            await event.answer(get_text("channel.required", lang, channel_url=settings.CHANNEL_URL), show_alert=True)

        return None
