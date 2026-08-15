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


# ══════════════════════════════════════════════════════════════
# NAVIGATION WHITELIST
# Tugmalar va commandalar — AI holatidan qat'i nazar ishlaydi
# ══════════════════════════════════════════════════════════════

NAVIGATION_WHITELIST = {
    # ─── ASOSIY MENYU (Registered) ──────────────────────
    "👤 Profil", "👤 Профиль", "👤 Profile",
    "⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings",
    "📖 Qo'llanma", "📖 Руководство", "📖 Guide",
    "📨 Admin ga xabar", "📨 Написать админу", "📨 Message admin",
    "📚 Darsliklar", "📚 Учебные материалы", "📚 Lessons",              # ⭐ YANGI
    "🧪 Test's (English QUIZ)", "🧪 Тесты (English QUIZ)",              # ⭐ YANGI

    # ─── SUBMENU: Sozlamalar ───────────────────────────
    "🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language",
    "🤖 AI ON/OFF", "🤖 AI ВКЛ/ВЫКЛ", "🤖 AI Yoqish/O'chirish",
    "🚪 Log Out", "🚪 Выйти", "🚪 Chiqish",

    # ─── SUBMENU: Qo'llanma / About ───────────────────
    "🤖 Bot bo'yicha", "🤖 О боте", "🤖 About Bot",
    "🧠 AI bo'yicha", "🧠 Об AI", "🧠 About AI",
    "🔗 Havolalar", "🔗 Ссылки", "🔗 Links",
    "🌐 Ecosystem Haqida", "🌐 Об экосистеме", "🌐 About Ecosystem",
    "❓ FAQ", "❓ ЧаВО",

    # ─── SUBMENU: Darsliklar (content_submenu_kb) ─────
    "🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson",
    "📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons",

    # ─── SUBMENU: Test's — CEFR darajalar ──────────────
    "A0", "A1", "A2", "B1", "B2", "C1", "C2",                           # ⭐ YANGI

    # ─── UNIVERSAL: Back / Cancel / Yes/No ─────────────
    "🏠 Bosh menyu", "🏠 Главное меню", "🏠 Home",
    "⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish",
    "❌ Bekor qilish", "❌ Отмена", "❌ Cancel",
    "✅ Ha", "✅ Да", "✅ Yes",
    "❌ Yo'q", "❌ Нет", "❌ No",

    # ─── COMMANDS ──────────────────────────────────────
    "/start", "/menu", "/profile", "/settings", "/help",
    "/video", "/file", "/quiz", "/register",                               # ⭐ /quiz YANGI
    "register",
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

        # ✅ Navigation tugmalari va commandalar — doim o'tadi
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

        # ✅ FIX: Faqat AI state'larda bo'lsa tekshir
        current_state = await state.get_state()
        ai_states = {"AIChat:waiting_message", "AIAgent:conversation"}
        if current_state and current_state not in ai_states:
            return await handler(event, data)

