"""Bot Guard middleware — check if bot is globally enabled.

Phase 5: Check global BOT_ENABLED setting before processing messages
- If BOT_ENABLED = false, only admins can use the bot
- Skips /start and /register commands to allow login flow
"""

import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from bot.config import settings, API_BASE_URL
import httpx

logger = logging.getLogger(__name__)

# Cache for global settings (to avoid API call on every message)
_settings_cache = {"BOT_ENABLED": "true", "_ts": 0}
_cache_ttl = 60  # 1 minute


async def get_global_bot_status():
    """Fetch global BOT_ENABLED setting from backend."""
    import time
    
    current_time = time.time()
    if current_time - _settings_cache.get("_ts", 0) < _cache_ttl:
        return _settings_cache.get("BOT_ENABLED", "true")
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{API_BASE_URL}/settings/global/BOT_ENABLED")
            if response.status_code == 200:
                data = response.json()
                value = data.get("value", "true")
                _settings_cache["BOT_ENABLED"] = value
                _settings_cache["_ts"] = current_time
                return value
    except Exception as e:
        logger.debug(f"Failed to fetch BOT_ENABLED setting (expected if backend offline): {e}")
        # Default to enabled if API unreachable
        return "true"
    
    # Return cached value or default
    return _settings_cache.get("BOT_ENABLED", "true")


class BotGuardMiddleware(BaseMiddleware):
    """Check if bot is globally enabled."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Only check messages and callbacks
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        # Get user_id
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            # Skip auth commands (allow registration flow)
            if event.text and event.text.strip().startswith(("/start", "/register", "/login")):
                return await handler(event, data)
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if not user_id:
            return await handler(event, data)
        
        # Admins always bypass bot guard
        if user_id in settings.admin_ids_list:
            return await handler(event, data)
        
        # Check global bot status
        try:
            bot_enabled = await get_global_bot_status()
            
            if bot_enabled.lower() == "false":
                logger.info(f"Bot disabled globally, user {user_id} blocked")
                
                if isinstance(event, Message):
                    await event.answer(
                        "🛑 <b>Bot hozircha ta'mirlanmoqda.</b>\n\n"
                        "Iltimos, keyin qayta urinib ko'ring.",
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        "🛑 Bot hozircha ta'mirlanmoqda. Keyin qayta urinib ko'ring.",
                        show_alert=True
                    )
                
                return None
        except Exception as e:
            logger.error(f"Bot guard error: {e}")
            # Fail-open: if API unreachable, allow the request
        
        return await handler(event, data)
