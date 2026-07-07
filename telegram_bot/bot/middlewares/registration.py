"""Registration middleware — check FSM state and route accordingly.

Rules:
- /start command, callbacks, contact sharing always pass
- FSM states (StartSection, RegistrationFSM, MenuSection, RegisteredSection) pass
- Unregistered users: AI teacher access + every 3rd message reminder
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from bot.states.registration import (
    StartSection, RegistrationFSM, MenuSection, RegisteredSection,
    RegisterFSM, LoginFSM, AuthFSM,
)
from bot.utils.i18n import get_text
from bot.config import settings

# Counter for unregistered users — send reminder every 3 messages
_user_message_count: Dict[int, int] = {}


class RegistrationMiddleware(BaseMiddleware):
    """Check registration state and route accordingly."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        state: FSMContext = data.get("state")
        if not state:
            return await handler(event, data)

        # Get current state
        current_state = await state.get_state()

        # ─── ALLOWED STATES — these always pass ───────────────
        allowed_states = [
            StartSection.language_selection.state,
            StartSection.main_menu.state,
            RegistrationFSM.phone_request.state,
            RegistrationFSM.phone_verified.state,
            RegistrationFSM.waiting_name.state,
            RegistrationFSM.waiting_birthdate.state,
            RegistrationFSM.waiting_level.state,
            RegistrationFSM.confirmation.state,
            AuthFSM.requesting_contact.state,
            AuthFSM.waiting_password.state,
            AuthFSM.waiting_name.state,
            AuthFSM.waiting_email.state,
            AuthFSM.waiting_password_new.state,
            AuthFSM.waiting_confirm_password.state,
            AuthFSM.confirmation.state,
            RegisterFSM.waiting_name.state,
            RegisterFSM.waiting_email.state,
            RegisterFSM.waiting_password.state,
            RegisterFSM.confirmation.state,
            LoginFSM.waiting_contact_or_email.state,
            LoginFSM.waiting_password.state,
            MenuSection.idle.state,
            MenuSection.language_selection.state,
            MenuSection.about_us.state,
            MenuSection.guide.state,
            MenuSection.contact_admin.state,
            MenuSection.settings.state,
            MenuSection.profile.state,
            MenuSection.video_lessons.state,
            MenuSection.file_lessons.state,
            RegisteredSection.main_menu.state,
            RegisteredSection.idle.state,
        ]

        if current_state in allowed_states:
            return await handler(event, data)

        # ─── ALWAYS PASS for these event types ────────────────
        if isinstance(event, Message):
            # /start and /help commands
            if event.text and event.text.startswith("/"):
                return await handler(event, data)

            # Contact sharing (phone number)
            if event.contact:
                return await handler(event, data)

        # ─── ALWAYS PASS for callbacks ──────────────────────
        if isinstance(event, CallbackQuery):
            callback_data = event.data
            if callback_data:
                always_pass_prefixes = (
                    "lang_", "level_", "menu_", "about_", "guide_",
                    "back_to_", "phone_", "reg_", "confirm_",
                    "settings_",
                )
                if callback_data.startswith(always_pass_prefixes):
                    return await handler(event, data)

        # ─── UNREGISTERED USER — allow AI teacher + reminders ──
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            # Track and optionally allow through + remind
            _user_message_count[user_id] = _user_message_count.get(user_id, 0) + 1
            should_remind = _user_message_count[user_id] % 3 == 0

            if isinstance(event, Message):
                lang = "uz"
                user_data = await state.get_data()
                if user_data:
                    lang = user_data.get("lang", "uz")

                # Trial counter (default from settings)
                trial = user_data.get("ai_trial_count", settings.AI_TRIAL_LIMIT)
                if trial <= 0:
                    # No trials left — show CTA/fallback and block
                    await event.answer(get_text("ai_fallback_teacher", lang))
                    return None

                # Decrement trial and allow through
                await state.update_data(ai_trial_count=trial - 1)

                if should_remind:
                    await event.answer(get_text("ai_fallback_reminder", lang))

                return await handler(event, data)

        # ─── Fallback — block with message ──────────────────
        if isinstance(event, Message):
            lang = "uz"
            user_data = await state.get_data()
            if user_data:
                lang = user_data.get("lang", "uz")
            await event.answer(get_text("ai_fallback_teacher", lang))

        return await handler(event, data)

