"""Reply keyboards for Myestro Telegram Bot."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def language_selection_keyboard() -> ReplyKeyboardMarkup:
    """3 tilda language selection keyboard (for /start)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek")],
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇬🇧 English")],
        ],
        resize_keyboard=True,
    )


# ══════════════════════════════════════════════════════════════
# DEPRECATED KEYBOARDS
# ══════════════════════════════════════════════════════════════
# These functions are deprecated. Use ColoredKeyboard from
# bot.keyboards.orange_keyboard instead:
#   - ColoredKeyboard.reply_main_menu(lang)  → replaces main_menu_keyboard()
#   - ColoredKeyboard.reply_main_menu(lang)  → replaces registered_menu_keyboard()
#   - ColoredKeyboard.reply_contact(lang)    → replaces contact_request_keyboard()
# ══════════════════════════════════════════════════════════════

# def main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
#     """DEPRECATED: Use ColoredKeyboard.reply_main_menu() instead."""
#     if lang == "uz":
#         buttons = [
#             ["📝 Register/Login", "ℹ️ Biz haqimizda"],
#             ["📖 Qo'llanma", "🌐 Til/Language"],
#             ["📨 Admin ga xabar"],
#         ]
#     elif lang == "ru":
#         buttons = [
#             ["📝 Регистрация/Вход", "ℹ️ О нас"],
#             ["📖 Руководство", "🌐 Язык"],
#             ["📨 Написать админу"],
#         ]
#     else:  # en
#         buttons = [
#             ["📝 Register/Login", "ℹ️ About us"],
#             ["📖 Guide", "🌐 Language"],
#             ["📨 Message admin"],
#         ]
#
#     return ReplyKeyboardMarkup(
#         keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons],
#         resize_keyboard=True,
#     )


# def registered_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
#     """DEPRECATED: Use ColoredKeyboard.reply_main_menu() instead."""
#     if lang == "uz":
#         buttons = [
#             ["👤 Profil", "⚙️ Sozlamalar"],
#             ["📖 Qo'llanma", "📨 Admin ga xabar"],
#             ["🎬 Video Darslik", "📁 File Darsliklar"],
#         ]
#     elif lang == "ru":
#         buttons = [
#             ["👤 Профиль", "⚙️ Настройки"],
#             ["📖 Руководство", "📨 Написать админу"],
#             ["🎬 Видеоурок", "📁 Файлы уроков"],
#         ]
#     else:  # en
#         buttons = [
#             ["👤 Profile", "⚙️ Settings"],
#             ["📖 Guide", "📨 Message admin"],
#             ["🎬 Video Lesson", "📁 File Lessons"],
#         ]
#
#     return ReplyKeyboardMarkup(
#         keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons],
#         resize_keyboard=True,
#     )


def contact_request_keyboard() -> ReplyKeyboardMarkup:
    """Phone number sharing keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)],
        ],
        resize_keyboard=True,
    )


def skip_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Skip button for optional fields."""
    if lang == "uz":
        text = "⏭️ Skip"
    elif lang == "ru":
        text = "⏭️ Пропустить"
    else:
        text = "⏭️ Skip"
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text)]],
        resize_keyboard=True,
    )


def confirm_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Confirmation keyboard: Tasdiqlash / Boshidan."""
    if lang == "uz":
        buttons = [["✅ Tasdiqlash", "🔄 Boshidan to'ldirish"]]
    elif lang == "ru":
        buttons = [["✅ Подтвердить", "🔄 Заполнить заново"]]
    else:
        buttons = [["✅ Confirm", "🔄 Start over"]]
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons],
        resize_keyboard=True,
    )


def lesson_numbers_keyboard(lesson_ids: list, lang: str = "uz") -> ReplyKeyboardMarkup:
    """Numeric keyboard for lesson selection (max 3 per row)."""
    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")
    keyboard = []
    row = []
    for i, lid in enumerate(lesson_ids):
        row.append(KeyboardButton(text=str(lid)))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([KeyboardButton(text=back_text)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


remove_keyboard = ReplyKeyboardRemove()