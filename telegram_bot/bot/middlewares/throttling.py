"""Throttling middleware — rate limiting for auth/contact handlers.

Limits each user to N requests per time window to prevent brute-force attacks.
Uses in-memory storage (no Redis dependency).
"""

import time
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)

# Rate limit configuration
RATE_LIMIT = 5       # Max requests per window
RATE_WINDOW = 60     # Time window in seconds

# Per-user rate tracking: {user_id: [timestamp1, timestamp2, ...]}
_rate_tracker: Dict[int, list] = {}


class ThrottlingMiddleware(BaseMiddleware):
    """Rate limiting middleware for auth and contact handlers.

    Tracks message frequency per user_id and blocks requests
    that exceed the configured limit within the time window.
    """

    def __init__(
        self,
        rate_limit: int = RATE_LIMIT,
        rate_window: int = RATE_WINDOW,
    ):
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        super().__init__()

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
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if not user_id:
            return await handler(event, data)

        # Check rate limit
        if self._is_rate_limited(user_id):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            lang = "uz"

            # Try to get language from state
            state = data.get("state")
            if state:
                user_data = await state.get_data()
                lang = user_data.get("lang", "uz")

            if isinstance(event, Message):
                await event.answer(
                    get_text("error.rate_limit", lang),
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    get_text("error.rate_limit", lang),
                    show_alert=True,
                )

            return None

        # Track this request
        self._track_request(user_id)

        return await handler(event, data)

    def _is_rate_limited(self, user_id: int) -> bool:
        """Check if user has exceeded the rate limit."""
        now = time.time()
        timestamps = _rate_tracker.get(user_id, [])

        # Remove old timestamps outside the window
        timestamps = [t for t in timestamps if now - t < self.rate_window]
        _rate_tracker[user_id] = timestamps

        # Check if limit exceeded
        return len(timestamps) >= self.rate_limit

    def _track_request(self, user_id: int) -> None:
        """Record a new request timestamp for the user."""
        now = time.time()
        if user_id not in _rate_tracker:
            _rate_tracker[user_id] = []
        _rate_tracker[user_id].append(now)