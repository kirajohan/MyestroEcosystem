"""AI Guard middleware — AI holatidan qat'i nazar navigatsiyani ta'minlaydi.

Reminder FSM holatlari va tugmalari ham whitelist'ga qo'shildi.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.fsm.context import FSMContext

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
    "📚 Darsliklar", "📚 Учебные материалы", "📚 Lessons",
    "🧪 Test (English QUIZ)", "🧪 Тест (English QUIZ)", "🧪 Тесты (English QUIZ)",

    # ─── SUBMENU: Sozlamalar ───────────────────────────
    "🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language",
    "🤖 AI ON/OFF", "🤖 AI ВКЛ/ВЫКЛ", "🤖 AI Yoqish/O'chirish",
    "🚪 Log Out", "🚪 Выйти", "🚪 Chiqish",

    # ─── SUBMENU: Eslatmalar (Reminders) ⭐ YANGI ──────
    "⏰ Eslatmalar", "⏰ Напоминания", "⏰ Reminders",
    "➕ Yangi eslatma", "➕ Новое напоминание", "➕ New reminder",
    "📋 Mening eslatmalarim", "📋 Мои напоминания", "📋 My reminders",
    "🗑️ Barchasini o'chirish", "🗑️ Удалить все", "🗑️ Delete all",

    # ─── Reminder turlari (reminder_type_kb) ───────────
    "1️⃣ Bir martalik", "1️⃣ Одноразовое", "1️⃣ One-time",
    "🔁 Har kuni", "🔁 Каждый день", "🔁 Daily",
    "📅 Har hafta", "📅 Каждую неделю", "📅 Weekly",

    # ─── Hafta kunlari (reminder_day_kb) ───────────────
    # O'zbek
    "Dushanba", "Seshanba", "Chorshanba", "Payshanba",
    "Juma", "Shanba", "Yakshanba",
    # Rus
    "Понедельник", "Вторник", "Среда", "Четверг",
    "Пятница", "Суббота", "Воскресенье",
    # Ingliz
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",

    # ─── SUBMENU: Qo'llanma / About ───────────────────
    "🤖 Bot bo'yicha", "🤖 О боте", "🤖 About Bot",
    "📝 Register", "📝 Регистрация",
    "🧠 AI bo'yicha", "🧠 Об AI", "🧠 About AI",
    "🔗 Havolalar", "🔗 Ссылки", "🔗 Links",
    "🌐 Ecosystem Haqida", "🌐 Об экосистеме", "🌐 About Ecosystem",
    "❓ FAQ", "❓ ЧаВО",

    # ─── SUBMENU: Darsliklar (content_submenu_kb) ─────
    "🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson",
    "📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons",

    # ─── SUBMENU: Test's — CEFR darajalar ──────────────
    "A0", "A1", "A2", "B1", "B2", "C1", "C2",

    # ─── UNIVERSAL: Back / Cancel / Yes/No ─────────────
    "🏠 Bosh menyu", "🏠 Главное меню", "🏠 Home",
    "⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish",
    "❌ Bekor qilish", "❌ Отмена", "❌ Cancel",
    "✅ Ha", "✅ Да", "✅ Yes",
    "❌ Yo'q", "❌ Нет", "❌ No",

    # ─── COMMANDS ──────────────────────────────────────
    "/start", "/menu", "/profile", "/settings", "/help",
    "/video", "/file", "/quiz", "/register", "/cancel",
    "register",
}


# ══════════════════════════════════════════════════════════════
# NON-AI FSM STATES
# Bu holatlarda AI chetlab o'tiladi (foydalanuvchi oddiy matn yozadi)
# ══════════════════════════════════════════════════════════════

NON_AI_STATES_PREFIX = (
    "ReminderFSM:",      # ⭐ Eslatmalar FSM
    "RegistrationFSM:",  # Ro'yxatdan o'tish
    "AuthFSM:",          # Autentifikatsiya
    "RegisterFSM:",      # Register
    "LoginFSM:",         # Login
    "ProfileEditFSM:",   # Profilni tahrirlash
    "MenuSection:contact_admin",  # Admin bilan bog'lanish
)


class AIGuardMiddleware(BaseMiddleware):
    """AI Guard — AI suhbat holatida bo'lmagan xabarlarni chetlab o'tadi."""

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

        text = (event.text or "").strip()
        state: FSMContext = data.get("state")
        current_state = await state.get_state() if state else None

        # DEBUG LOG
        logger.debug(f"🔍 AIGuard: Text='{text[:30]}' | State={current_state}")

        # ─── 1. Whitelist yoki Command tekshiruvi ─────────────
        if text in NAVIGATION_WHITELIST or text.startswith("/"):
            logger.debug(f"✅ WHITELIST: {text}")
            return await handler(event, data)

        # ─── 2. Ro'yxatdan o'tganlik tekshiruvi ───────────────
        user_data = await state.get_data() if state else {}
        if not user_data.get("registration_complete", False):
            logger.debug("🚫 Ro'yxatdan o'tmagan — o'tkazildi")
            return await handler(event, data)

        # ─── 3. FSM State tekshiruvi ──────────────────────────
        # Agar FSM "non-AI" holatda bo'lsa (masalan, ReminderFSM)
        # AI chetlab o'tiladi va oddiy handler ishlaydi
        if current_state:
            # Non-AI holatlarni tekshirish
            for prefix in NON_AI_STATES_PREFIX:
                if current_state.startswith(prefix):
                    logger.debug(f"🚫 Non-AI state: {current_state} — o'tkazildi")
                    return await handler(event, data)
            
            # MenuSection ichidagi maxsus holatlar
            menu_non_ai = {
                "MenuSection:settings",
                "MenuSection:about_us",
                "MenuSection:guide",
                "MenuSection:language_selection",
            }
            if current_state in menu_non_ai:
                logger.debug(f"🚫 Menu state: {current_state} — o'tkazildi")
                return await handler(event, data)

        # ─── 4. AI suhbat holatini tekshirish ─────────────────
        # Faqat shu holatlarda AI to'liq ishlaydi
        ai_states = {
            "AIChat:waiting_message",
            "AIAgent:conversation",
            "RegisteredSection:main_menu",  # Asosiy menyuda AI ishlaydi
            "RegisteredSection:idle",
            None,  # State yo'q bo'lsa ham AI ishlashi mumkin
        }
        
        if current_state not in ai_states:
            logger.debug(f"🚫 State AI emas: {current_state}")
            return await handler(event, data)

        # ─── AI ISHLASHI KERAK ────────────────────────────────
        logger.debug("🤖 AI ishga tushmoqda...")
        return await handler(event, data)