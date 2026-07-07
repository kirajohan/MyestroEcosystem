"""Channel subscription middleware — check if user is subscribed to required channel.

Phase 2: After registration, user must join channel to use bot.
- Skips check for: /start, /register, /login commands
- Admins bypass this check
- Registered users are checked on all other messages
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject, ChatMemberUpdated
from aiogram.fsm.context import FSMContext
from bot.config import settings
from bot.utils.i18n import get_text

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
            return await handler(event, data)

        # Skip for ChatMemberUpdated (channel join events)
        if isinstance(event, ChatMemberUpdated):
            return await handler(event, data)

        # Get user_id
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            # Skip auth commands (let registration handlers process freely)
            if event.text and event.text.strip().startswith(("/start", "/register", "/login")):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            # Skip channel join callback
            if event.data and event.data.startswith("channel_joined"):
                return await handler(event, data)

        if not user_id:
            return await handler(event, data)

        # Admins always bypass channel check
        if user_id in settings.admin_ids_list:
            return await handler(event, data)

        # Check channel membership
        try:
            member = await event.bot.get_chat_member(int(settings.CHANNEL_ID), user_id)
            
            # Valid statuses: member, administrator, creator
            if member.status in {"member", "administrator", "creator"}:
                return await handler(event, data)
            
        except Exception as e:
            logger.warning(f"Channel check failed for user {user_id}: {e}")
            # On error: allow through (graceful fallback)
            return await handler(event, data)

        # User NOT in channel — show subscription prompt
        state: FSMContext = data.get("state")
        lang = "uz"
        if state:
            user_data = await state.get_data()
            lang = user_data.get("lang", "uz")

        if isinstance(event, Message):
            await event.answer(
                f"❌ <b>Kanalga a'zo bo'lishingiz kerak!</b>\n\n"
                f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Kanalga a'zo bo'lish</a>\n\n"
                "A'zo bo'lganidan keyin yana urinib ko'ring."
            )
        elif isinstance(event, CallbackQuery):
            await event.answer(
                f"❌ Kanalga a'zo bo'lishingiz kerak: https://t.me/{settings.CHANNEL_USERNAME}",
                show_alert=True
            )

        return None
