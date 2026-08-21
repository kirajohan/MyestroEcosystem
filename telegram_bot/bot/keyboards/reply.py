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
    builder.adjust(1)
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
        "uz": ["👤 Profil", "⚙️ Sozlamalar", "📖 Qo'llanma", "📨 Admin ga xabar", "📚 Darsliklar", "🧪 Test's (English QUIZ)"],
        "ru": ["👤 Профиль", "⚙️ Настройки", "📖 Руководство", "📨 Написать админу", "📚 Учебные материалы", "🧪 Тесты (English QUIZ)"],
        "en": ["👤 Profile", "⚙️ Settings", "📖 Guide", "📨 Message admin", "📚 Lessons", "🧪 Test's (English QUIZ)"],
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
        "uz": {"lang": "🌐 Til o'zgartirish", "ai": "🤖 AI ON/OFF" },
        "ru": {"lang": "🌐 Сменить язык", "ai": "🤖 AI ВКЛ/ВЫКЛ"},
        "en": {"lang": "🌐 Change Language", "ai": "🤖 AI ON/OFF" },
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["lang"], style="primary"),
        StyledKeyboardButton(text=t["ai"], style="primary"),
    )
    builder.add(
        StyledKeyboardButton(text="⬅️ Orqaga", style="danger"),
    )
    builder.adjust(2,1)
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
            "language": "🌐 Til/Language",
            "about": "ℹ️ Biz haqimizda",
            "guide": "📖 Qo'llanma",
            "admin": "📨 Admin ga xabar",
        },
        "ru": {
            "start": "📝 Регистрация",
            "language": "🌐 Язык",
            "about": "ℹ️ О нас",
            "guide": "📖 Руководство",
            "admin": "📨 Написать админу",
        },
        "en": {
            "start": "📝 Register",
            "language": "🌐 Language",
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

def profile_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Profile screen keyboard: Edit + Back."""
    texts = {
        "uz": {"edit": "✏️ Tahrirlash", "back": "⬅️ Orqaga"},
        "ru": {"edit": "✏️ Редактировать", "back": "⬅️ Назад"},
        "en": {"edit": "✏️ Edit", "back": "⬅️ Back"},
    }
    t = texts.get(lang, texts["uz"])

    builder = ReplyKeyboardBuilder()
    builder.add(
        StyledKeyboardButton(text=t["edit"], style="primary"),
        StyledKeyboardButton(text=t["back"], style="danger"),
    )
    builder.adjust(1)
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