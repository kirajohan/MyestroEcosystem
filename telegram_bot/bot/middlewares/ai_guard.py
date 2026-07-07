"""AI Guard middleware — check if AI is enabled for user/global.

Before processing any text/voice message, checks:
1. Global AI toggle (system_settings)
2. User-level AI toggle (users.ai_enabled)

If AI is disabled, the message is blocked with a notification.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.fsm.context import FSMContext
from bot.config import API_BASE_URL
import httpx


import logging
logger = logging.getLogger(__name__)

class AIGuardMiddleware(BaseMiddleware):
    """
    Check AI availability before allowing AI handler to process.
    Skips check for unregistered users and non-text/voice messages.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Only check text and voice messages
        if not isinstance(event, Message):
            return await handler(event, data)

        if event.content_type not in {"text", "voice"}:
            return await handler(event, data)

        # Skip commands
        if event.text and event.text.startswith("/"):
            return await handler(event, data)

        # Get user state to check if registered
        state: FSMContext = data.get("state")
        user_data = {}
        if state:
            user_data = await state.get_data()

        registration_complete = user_data.get("registration_complete", False)

        # Only check AI status for registered users
        if not registration_complete:
            return await handler(event, data)

        user_id = event.from_user.id
        lang = user_data.get("lang", "uz")

        # Check AI status via Backend API
        try:
            logger.debug(f"[AIGUARD] Checking user {user_id} via {API_BASE_URL}/sync/user/{user_id}")
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Get user data from sync API
                response = await client.get(
                    f"{API_BASE_URL}/sync/user/{user_id}",
                )

                logger.debug(f"[AIGUARD] sync/user response: {response.status_code}")
                if response.status_code == 200:
                    user_data_api = response.json()
                    from bot.utils.i18n import get_text

                    # Check user-level AI toggle
                    if not user_data_api.get("ai_enabled", True):
                        logger.info(f"[AIGUARD] AI disabled for user {user_id}")
                        print(f"[AIGUARD] AI disabled for user {user_id}")
                        await event.answer(get_text("ai.user_off", lang))
                        return None

                    # Check global AI toggle (admin panel'dan o'chirilgan bo'lsa)
                    try:
                        async with httpx.AsyncClient(timeout=3.0) as client:
                            logger.debug(f"[AIGUARD] Checking global AI via {API_BASE_URL}/settings/ai-public")
                            global_resp = await client.get(f"{API_BASE_URL}/settings/ai-public")
                            logger.debug(f"[AIGUARD] settings/ai-public response: {global_resp.status_code}")
                            if global_resp.status_code == 200:
                                global_setting = global_resp.json()
                                if global_setting.get("value", "true").lower() == "false":
                                    logger.info("[AIGUARD] Global AI disabled")
                                    await event.answer(get_text("ai.global_off", lang))
                                    return None
                    except Exception as e:
                        logger.error(f"[AIGUARD] error checking global AI: {e}")
                else:
                    # Fallback: check from local state
                    if not user_data.get("ai_enabled", True):
                        from bot.utils.i18n import get_text
                        logger.info(f"[AIGUARD] AI disabled in local state for user {user_id}")
                        await event.answer(get_text("ai.user_off", lang))
                        return None

        except Exception as e:
            # Fail-open: if Backend is unreachable, allow the request
            logger.error(f"[AIGUARD] exception when checking AI status: {e}")
            pass

        return await handler(event, data)

