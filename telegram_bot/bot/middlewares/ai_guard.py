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
# ... existing imports ...

# Define navigation texts that should ALWAYS work regardless of AI status
# Add all main menu button texts here (match your bot_texts CMS values)
NAVIGATION_WHITELIST = {
    "👤 Profil", "⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings", "📖 Qo'llanma", "🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language","🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson","🤖 Bot bo'yicha", "🤖 О боте", "🤖 About Bot"
    "🏠 Bosh menyu", "⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish", "❌ Bekor qilish","🤖 AI ON/OFF", "🤖 AI ВКЛ/ВЫКЛ", "🤖 AI Yoqish/O'chirish","🚪 Log Out", "🚪 Выйти", "🚪 Chiqish","📨 Admin ga xabar", "📨 Написать админу", "📨 Message admin",
    "📖 Qo'llanma", "📖 Руководство", "📖 Guide", "🧠 AI bo'yicha", "🧠 Об AI", "🧠 About AI", "/start", "/menu", "/profile", "/settings", "/help" ,'/video',
    "🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language","🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson","📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons"
    "✅ Ha", "✅ Да", "✅ Yes","❌ Yo'q", "❌ Нет", "❌ No", "/file", "register","/profile"
}

class AIGuardMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        if event.content_type not in {"text", "voice"}:
            return await handler(event, data)

        # ✅ FIX: Allow navigation buttons and commands to pass through
        text = (event.text or "").strip()
        if text in NAVIGATION_WHITELIST or text.startswith("/"):
            return await handler(event, data)

        # ... existing registration check ...
        state: FSMContext = data.get("state")
        user_data = {}
        if state:
            user_data = await state.get_data()

        registration_complete = user_data.get("registration_complete", False)
        if not registration_complete:
            return await handler(event, data)

        # ✅ FIX: Only block if user is NOT in an AI-related FSM state
        # This prevents blocking settings toggles or other non-AI text inputs
        current_state = await state.get_state()
        ai_states = {"AIChat:waiting_message", "AIAgent:conversation"}  # Adjust to your actual state names
        if current_state and current_state not in ai_states:
            return await handler(event, data)

        # ... rest of existing AI check logic (sync/user API call) ...