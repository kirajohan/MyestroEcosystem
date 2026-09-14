"""Reply keyboards for Myestro Telegram Bot - REPLY KEYBOARD ONLY."""

from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bot.keyboards.extended_buttons import StyledKeyboardButton
from typing import List, Dict


# ─── LANGUAGE SELECTION ──────────────────────────────────────

def language_selection(include_back: bool = False) -> ReplyKeyboardMarkup:
    """Language selection keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text="🇺🇿 O'zbek", style="primary"),
        StyledKeyboardButton(text="🇷🇺 Русский", style="primary"),
        StyledKeyboardButton(text="🇬🇧 English", style="primary"),
    )
    if include_back:
        builder.add(
            StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
        )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def language_switch_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Language switch with back button."""
    from bot.utils.i18n import get_text
    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text="🇺🇿 O'zbek", style="primary"),
        StyledKeyboardButton(text="🇷🇺 Русский", style="danger"),
        StyledKeyboardButton(text="🇬🇧 English", style="success"),
    )
    builder.add(
        StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ─── ABOUT US ────────────────────────────────────────────────

def about_us_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """About us submenu."""
    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text="🔗 Havolalar", style="success"),
        StyledKeyboardButton(text="🌐 Ecosystem Haqida", style="success"),
        StyledKeyboardButton(text="❓ FAQ", style="success"),
    )
    builder.add(
        StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ─── GUIDE ───────────────────────────────────────────────────

def guide_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Guide submenu."""
    texts = {
        "uz": {"bot": "🤖 Bot bo'yicha", "ai": "🧠 AI bo'yicha", "faq": "❓ FAQ"},
        "ru": {"bot": "🤖 О боте", "ai": "🧠 Об AI", "faq": "❓ FAQ"},
        "en": {"bot": "🤖 About Bot", "ai": "🧠 About AI", "faq": "❓ FAQ"},
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["bot"], style="primary"),
        StyledKeyboardButton(text=t["ai"], style="primary"),
        StyledKeyboardButton(text=t["faq"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# ─── CEFR LEVEL SELECTION ────────────────────────────────────

def cefr_level_selection() -> ReplyKeyboardMarkup:
    """CEFR level selection."""
    builder = ReplyKeyboardBuilder()
    levels = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]
    for level in levels:
        builder.add(
            StyledKeyboardButton(text=level, style="primary"),
        )
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


def content_submenu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Darsliklar submenu — Video + File (bir joyda)."""
    texts = {
        "uz": {
            "video": "🎬 Video Darslik",
            "file": "📁 File Darsliklar",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "video": "🎬 Видеоурок",
            "file": "📁 Файлы уроков",
            "back": "⬅️ Назад",
        },
        "en": {
            "video": "🎬 Video Lesson",
            "file": "📁 File Lessons",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["video"], style="success"),
        StyledKeyboardButton(text=t["file"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

# ─── REGISTERED USER MAIN MENU ──────────────────────────────

def registered_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Main menu for REGISTERED users."""
    texts = {
        "uz": ["👤 Profil", "⚙️ Sozlamalar", "📖 Qo'llanma", "📨 Admin ga xabar", "📚 Darsliklar", "🧪 Test (English QUIZ)"],
        "ru": ["👤 Профиль", "⚙️ Настройки", "📖 Руководство", "📨 Написать админу", "📚 Учебные материалы", "🧪 Тест (English QUIZ)"],
        "en": ["👤 Profile", "⚙️ Settings", "📖 Guide", "📨 Message admin", "📚 Lessons", "🧪 Test (English QUIZ)"],
    }
    items = texts.get(lang, texts["uz"])
    # 5 ta qoladi (primary, primary, success, danger, success) + yangi Test's (primary)
    styles = ["primary", "primary", "success", "danger", "success", "primary"]

    builder = ReplyKeyboardBuilder()
    for text, style in zip(items, styles):
        builder.add(
            StyledKeyboardButton(text=text, style=style),
        )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# ─── SETTINGS ────────────────────────────────────────────────

def settings_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Settings submenu."""
    texts = {
        "uz": {
            "lang": "🌐 Til o'zgartirish", 
            "ai": "🤖 AI ON/OFF",
            "reminders": "⏰ Eslatmalar",  # ← YANGI
        },
        "ru": {
            "lang": "🌐 Сменить язык", 
            "ai": "🤖 AI ВКЛ/ВЫКЛ",
            "reminders": "⏰ Напоминания",
        },
        "en": {
            "lang": "🌐 Change Language", 
            "ai": "🤖 AI ON/OFF",
            "reminders": "⏰ Reminders",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["lang"], style="primary"),
        StyledKeyboardButton(text=t["ai"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["reminders"], style="success"),  # ← YANGI
    )
    builder.add(
        StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
    )
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


# ─── CONTACT REQUEST ────────────────────────────────────────

def contact_request_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Contact sharing request."""
    texts = {
        "uz": {"share": "📱 Raqam yuborish", "back": "⬅️ Orqaga"},
        "ru": {"share": "📱 Отправить номер", "back": "⬅️ Назад"},
        "en": {"share": "📱 Send phone", "back": "⬅️ Back"},
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["share"], request_contact=True, style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ─── REGISTRATION RESTART ──────────────────────────────────

def registration_restart_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Registration restart/back."""
    texts = {
        "uz": {"restart": "🔄 Boshidan boshlash", "back": "⬅️ Orqaga"},
        "ru": {"restart": "🔄 Начать заново", "back": "⬅️ Назад"},
        "en": {"restart": "🔄 Start over", "back": "⬅️ Back"},
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["restart"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ─── CONFIRMATION (YES/NO) ──────────────────────────────────

def confirm_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Yes/No confirmation."""
    texts = {
        "uz": {"yes": "✅ Ha", "no": "❌ Yo'q"},
        "ru": {"yes": "✅ Да", "no": "❌ Нет"},
        "en": {"yes": "✅ Yes", "no": "❌ No"},
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["yes"], style="success"),
        StyledKeyboardButton(text=t["no"], style="danger"),
    )
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# ─── MAIN MENU (NOT_REGISTERED) ─────────────────────────────

def main_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Main menu for NOT_REGISTERED users."""
    texts = {
        "uz": {
            "start": "📝 Register",
            "language": "🌐 Til o'zgartirish",
            "about": "ℹ️ Biz haqimizda",
            "guide": "📖 Qo'llanma",
            "admin": "📨 Admin ga xabar",
        },
        "ru": {
            "start": "📝 Регистрация",
            "language": "🌐 Сменить язык",
            "about": "ℹ️ О нас",
            "guide": "📖 Руководство",
            "admin": "📨 Написать админу",
        },
        "en": {
            "start": "📝 Register",
            "language": "🌐 Change Language",
            "about": "ℹ️ About us",
            "guide": "📖 Guide",
            "admin": "📨 Message admin",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["start"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["language"], style="success"),
        StyledKeyboardButton(text=t["about"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["guide"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["admin"], style="danger"),
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


# Alias for import in register.py
main_menu_kb = main_menu


# ─── ADMIN CONTACT ──────────────────────────────────────────

def admin_contact_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Admin contact session (send message + back)."""
    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# ─── PROFILE KEYBOARDS ──────────────────────────────────────

# ─── PROFILE KEYBOARDS ──────────────────────────────────────

def profile_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Profile screen keyboard: Edit + Change Password + Back."""
    texts = {
        "uz": {
            "edit": "✏️ Tahrirlash",
            "password": "🔑 Parolni o'zgartirish",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "edit": "✏️ Редактировать",
            "password": "🔑 Сменить пароль",
            "back": "⬅️ Назад",
        },
        "en": {
            "edit": "✏️ Edit",
            "password": "🔑 Change password",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["edit"], style="primary"),
        StyledKeyboardButton(text=t["password"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)


    

def profile_edit_fields_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Profile edit field selection keyboard."""
    texts = {
        "uz": {
            "name": "📝 Ism",
            "cefr": "📊 CEFR Level",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "name": "📝 Имя",
            "cefr": "📊 CEFR Level",
            "back": "⬅️ Назад",
        },
        "en": {
            "name": "📝 Name",
            "cefr": "📊 CEFR Level",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["name"], style="primary"),
        StyledKeyboardButton(text=t["cefr"], style="success"),
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(2,1)
    return builder.as_markup(resize_keyboard=True)


def cefr_level_selection_with_back(lang: str = "uz") -> ReplyKeyboardMarkup:
    """CEFR level selection with back button."""
    back_texts = {
        "uz": "⬅️ Orqaga",
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
    }
    back_text = back_texts.get(lang, back_texts["uz"])

    builder = ReplyKeyboardBuilder()

    levels = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]
    for level in levels:
        builder.add(
            StyledKeyboardButton(text=level, style="primary"),
        )

    builder.add(
        StyledKeyboardButton(text=back_text, style="danger"),
    )

    builder.adjust(3, 3, 2)
    return builder.as_markup(resize_keyboard=True)


# ─── SPECIAL: REMOVE KEYBOARD ──────────────────────────────

remove_keyboard = ReplyKeyboardRemove()


# ─── REMINDERS ───────────────────────────────────────────────

def reminders_main_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Eslatmalar asosiy menyusi."""
    texts = {
        "uz": {
            "add": "➕ Yangi eslatma",
            "list": "📋 Mening eslatmalarim",
            "delete_all": "🗑️ Barchasini o'chirish",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "add": "➕ Новое напоминание",
            "list": "📋 Мои напоминания",
            "delete_all": "🗑️ Удалить все",
            "back": "⬅️ Назад",
        },
        "en": {
            "add": "➕ New reminder",
            "list": "📋 My reminders",
            "delete_all": "🗑️ Delete all",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["add"], style="success"),
        StyledKeyboardButton(text=t["list"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["delete_all"], style="danger"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def reminder_type_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Eslatma turi tanlash."""
    texts = {
        "uz": {
            "once": "1️⃣ Bir martalik",
            "daily": "🔁 Har kuni",
            "weekly": "📅 Har hafta",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "once": "1️⃣ Одноразовое",
            "daily": "🔁 Каждый день",
            "weekly": "📅 Каждую неделю",
            "back": "⬅️ Назад",
        },
        "en": {
            "once": "1️⃣ One-time",
            "daily": "🔁 Daily",
            "weekly": "📅 Weekly",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["once"], style="primary"),
        StyledKeyboardButton(text=t["daily"], style="success"),
        StyledKeyboardButton(text=t["weekly"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(1, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def reminder_day_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Hafta kunlari."""
    texts = {
        "uz": ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba", "⬅️ Orqaga"],
        "ru": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье", "⬅️ Назад"],
        "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "⬅️ Back"],
    }
    items = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    for day in items[:-1]:
        builder.add(StyledKeyboardButton(text=day, style="primary"))
    builder.add(StyledKeyboardButton(text=items[-1], style="danger"))
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


def reminder_date_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Bir martalik eslatma uchun kun tanlash."""
    texts = {
        "uz": {
            "today": "📅 Bugun",
            "tomorrow": "📅 Ertaga",
            "custom": "📝 Boshqa kun",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "today": "📅 Сегодня",
            "tomorrow": "📅 Завтра",
            "custom": "📝 Другой день",
            "back": "⬅️ Назад",
        },
        "en": {
            "today": "📅 Today",
            "tomorrow": "📅 Tomorrow",
            "custom": "📝 Another day",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["today"], style="primary"),
        StyledKeyboardButton(text=t["tomorrow"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["custom"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)

def reminder_ai_choice_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """AI generatsiya qiladimi yoki statik matnmi?"""
    texts = {
        "uz": {
            "static": "📝 Oddiy matn (har kuni bir xil)",
            "ai": "🤖 AI har kuni yangi content",
            "back": "⬅️ Orqaga",
        },
        "ru": {
            "static": "📝 Обычный текст (каждый день одно)",
            "ai": "🤖 AI каждый день новый контент",
            "back": "⬅️ Назад",
        },
        "en": {
            "static": "📝 Static text (same every day)",
            "ai": "🤖 AI generates new content daily",
            "back": "⬅️ Back",
        },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["static"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text=t["ai"], style="success"),
    )
    builder.add(
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(1, 1, 1)
    return builder.as_markup(resize_keyboard=True)