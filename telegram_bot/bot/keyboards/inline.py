"""Inline keyboards for Myestro Telegram Bot."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


# ─── LANGUAGE SELECTION ──────────────────────────────────────

def language_selection(include_back: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    if include_back:
        builder.button(text="⬅️ Orqaga", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def language_switch_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Language switch with back button — used from Settings."""
    from bot.utils.i18n import get_text
    builder = InlineKeyboardBuilder()
    builder.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
    builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
    builder.button(text="🇬🇧 English", callback_data="lang_en")
    builder.button(text=get_text("back", lang), callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


# ─── CEFR LEVEL SELECTION ────────────────────────────────────

def cefr_level_selection() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    levels = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]
    for level in levels:
        builder.button(text=level, callback_data=f"level_{level}")
    builder.adjust(3)
    return builder.as_markup()


# ─── REGISTERED USER MAIN MENU ──────────────────────────────

def registered_menu_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline menu for REGISTERED users — updated with combined Lessons + Test."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": ["👤 Profil", "⚙️ Sozlamalar", "📨 Admin ga xabar", "📚 Darslar", "✅ Test"],
        "ru": ["👤 Профиль", "⚙️ Настройки",  "📨 Написать админу", "📚 Уроки", "✅ Тест"],
        "en": ["👤 Profile", "⚙️ Settings",  "📨 Message admin", "📚 Lessons", "✅ Test"],
    }
    items = texts.get(lang, texts["uz"])
    callbacks = ["menu_profile", "menu_settings", "menu_guide", "menu_admin_msg", "menu_lessons", "menu_test"]
    builder = InlineKeyboardBuilder()
    for text, cb in zip(items, callbacks):
        builder.button(text=text, callback_data=cb)
    builder.adjust(2)
    return builder.as_markup()


def about_us_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Biz haqimizda bo'limi uchun inline klaviatura."""
    builder = InlineKeyboardBuilder()
    
    # Masalan: Veb-sayt yoki admin havolasi tugmasi
    web_text = "🌐 Website" if lang == "en" else ("🌐 Веб-сайт" if lang == "ru" else "🌐 Veb-sayt")
    builder.button(text=web_text, url="https://myestro.uz")
    
    back_text = "⬅️ Back" if lang == "en" else ("⬅️ Назад" if lang == "ru" else "⬅️ Orqaga")
    builder.button(text=back_text, callback_data="back_to_menu")
    
    builder.adjust(1)
    return builder.as_markup()


# ─── SETTINGS ────────────────────────────────────────────────

def settings_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Settings menu: Language, AI ON/OFF, Log Out, Orqaga."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"lang": "🌐 Til o'zgartirish", "ai": "🤖 AI ON/OFF", "logout": "🚪 Log Out"},
        "ru": {"lang": "🌐 Сменить язык", "ai": "🤖 AI ВКЛ/ВЫКЛ", "logout": "🚪 Выйти"},
        "en": {"lang": "🌐 Change Language", "ai": "🤖 AI ON/OFF", "logout": "🚪 Log Out"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["lang"], callback_data="settings_language")
    builder.button(text=t["ai"], callback_data="settings_ai_toggle")
    builder.button(text=t["logout"], callback_data="settings_logout")
    builder.button(text=get_text("back", lang), callback_data="back_to_settings")
    builder.adjust(1)
    return builder.as_markup()


# ─── PHONE REQUEST ──────────────────────────────────────────

def phone_request_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Phone request: Share phone + Back."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"share": "📱 Raqam yuborish", "back": "⬅️ Orqaga qaytish"},
        "ru": {"share": "📱 Отправить номер", "back": "⬅️ Назад"},
        "en": {"share": "📱 Send number", "back": "⬅️ Go back"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["share"], callback_data="phone_share")
    builder.button(text=t["back"], callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── REGISTRATION ──────────────────────────────────────────

def registration_restart_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Registration: Boshidan boshlash + Orqaga."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"restart": "🔄 Boshidan boshlash", "back": "⬅️ Orqaga"},
        "ru": {"restart": "🔄 Начать заново", "back": "⬅️ Назад"},
        "en": {"restart": "🔄 Start over", "back": "⬅️ Back"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["restart"], callback_data="reg_restart")
    builder.button(text=t["back"], callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── CONFIRM ───────────────────────────────────────────────

def confirm_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"yes": "✅ Ha", "no": "❌ Yo'q"},
        "ru": {"yes": "✅ Да", "no": "❌ Нет"},
        "en": {"yes": "✅ Yes", "no": "❌ No"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["yes"], callback_data="confirm_yes")
    builder.button(text=t["no"], callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()


# ─── EXISTING (backward compatibility) ─────────────────────

def main_menu(lang: str = "uz") -> InlineKeyboardMarkup:
    """Legacy main menu — redirects to NOT_REGISTERED menu."""
    from bot.utils.i18n import get_text
    builder = InlineKeyboardBuilder()
    items = [
        ("teacher_chat", "teacher"),
        ("exams", "exams"),
        ("language", "language"),
        ("about_us", "about"),
        ("contact_admin", "admin_msg"),
    ]
    for text_key, callback in items:
        builder.button(text=get_text(text_key, lang), callback_data=f"menu_{callback}")
    builder.adjust(2)
    return builder.as_markup()


def exam_list(exams: List[Dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for exam in exams:
        title = exam.get("title", f"Exam #{exam.get('id')}")
        builder.button(text=title, callback_data=f"exam_{exam['id']}")
    builder.adjust(1)
    return builder.as_markup()


# ─── ADMIN CONTACT ──────────────────────────────────────────

def admin_contact_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Admin contact session: Orqaga (exit)."""
    from bot.utils.i18n import get_text
    builder = InlineKeyboardBuilder()
    builder.button(text=get_text("back", lang), callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── CHANNEL SUBSCRIPTION ────────────────────────────────────

def channel_subscribe_kb(lang: str = "uz", channel_url: str = "") -> InlineKeyboardMarkup:
    """Channel subscription prompt: Join channel + Check again.
    
    Args:
        lang: Language code (uz, ru, en)
        channel_url: Channel URL from .env (e.g., https://t.me/testmyestro or @testmyestro)
    """
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"join": "📢 Kanalga obuna bo'lish", "check": "✅ Obunani tekshirish"},
        "ru": {"join": "📢 Подписаться на канал", "check": "✅ Проверить подписку"},
        "en": {"join": "📢 Join channel", "check": "✅ Check subscription"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    
    # Clean up channel_url to get the proper link
    if channel_url:
        # Handle both https://t.me/testmyestro and @testmyestro formats
        clean_url = channel_url.rstrip('/').replace('https://t.me/', '').replace('http://t.me/', '').lstrip('@')
        channel_link = f"https://t.me/{clean_url}"
    else:
        channel_link = "https://t.me"
    
    builder.button(text=t["join"], url=channel_link)
    builder.button(text=t["check"], callback_data="channel_joined")
    builder.adjust(1)
    return builder.as_markup()

# ─── REGISTER / LOGIN ──────────────────────────────────────

def register_login_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Login choice: Contact or Email."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"contact": "📱 Telefon raqam bilan", "email": "📧 Email bilan"},
        "ru": {"contact": "📱 По номеру телефона", "email": "📧 По email"},
        "en": {"contact": "📱 By phone", "email": "📧 By email"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["contact"], callback_data="login_contact")
    builder.button(text=t["email"], callback_data="login_email")
    builder.adjust(1)
    return builder.as_markup()


# ─── LESSONS MENU ────────────────────────────────────────────

def lessons_menu_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Lessons sub-menu: Video lessons + File lessons + Back."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"video": "🎬 Video darslar", "file": "📁 Fayl darslar", "back": "⬅️ Orqaga"},
        "ru": {"video": "🎬 Видеоуроки", "file": "📁 Файловые уроки", "back": "⬅️ Назад"},
        "en": {"video": "🎬 Video Lessons", "file": "📁 File Lessons", "back": "⬅️ Back"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["video"], callback_data="lessons_video")
    builder.button(text=t["file"], callback_data="lessons_file")
    builder.button(text=t["back"], callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


# ─── TEST (CEFR LEVEL) ───────────────────────────────────────

def test_level_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """CEFR level selection grid: A1-A2-B1-B2 / C1-C2 + Back."""
    from bot.utils.i18n import get_text
    builder = InlineKeyboardBuilder()
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    for level in levels:
        builder.button(text=f"📚 {level}", callback_data=f"test_level_{level}")
    builder.button(text=get_text("back", lang), callback_data="back_to_menu")
    builder.adjust(3, 3, 1)
    return builder.as_markup()


def test_confirm_kb(lang: str = "uz", level: str = "A1") -> InlineKeyboardMarkup:
    """Test start confirmation: Start + Back to levels."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"start": "✅ Testni boshlash", "back": "⬅️ Darajani tanlash"},
        "ru": {"start": "✅ Начать тест", "back": "⬅️ Выбрать уровень"},
        "en": {"start": "✅ Start Test", "back": "⬅️ Select Level"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["start"], callback_data=f"test_start_{level}")
    builder.button(text=t["back"], callback_data="test_select_level")
    builder.adjust(1)
    return builder.as_markup()


def test_question_kb(options: list, question_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Test question options keyboard.
    
    Args:
        options: List of (label, is_correct) tuples for answer options.
        question_id: Current question ID for tracking.
        lang: Language code.
    """
    builder = InlineKeyboardBuilder()
    for i, (label, _) in enumerate(options):
        builder.button(text=label, callback_data=f"test_answer_{question_id}_{i}")
    builder.adjust(1)
    return builder.as_markup()


def test_results_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Test results actions: Repeat + Lessons + Menu."""
    from bot.utils.i18n import get_text
    texts = {
        "uz": {"repeat": "🔄 Qayta urinish", "lessons": "📚 Darslar", "menu": "🏠 Asosiy menyu"},
        "ru": {"repeat": "🔄 Попробовать снова", "lessons": "📚 Уроки", "menu": "🏠 Главное меню"},
        "en": {"repeat": "🔄 Try Again", "lessons": "📚 Lessons", "menu": "🏠 Main Menu"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.button(text=t["repeat"], callback_data="test_select_level")
    builder.button(text=t["lessons"], callback_data="menu_lessons")
    builder.button(text=t["menu"], callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()

