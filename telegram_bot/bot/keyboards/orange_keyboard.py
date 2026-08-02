# bot/keyboards/orange_keyboard.py

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from bot.keyboards.extended_buttons import StyledKeyboardButton, StyledInlineKeyboardButton
from typing import List, Literal

class ColoredKeyboard:
    """Color-themed keyboard factory — Blue (Primary), Red (Danger), Green (Success)."""
    
    # Color codes
    BLUE = "🔵"
    RED = "🔴"
    GREEN = "🟢"
    ICON_BACK = "⬅️"
    ICON_NEXT = "➡️"
    
    # ─── REPLY KEYBOARDS ───────────────────────────────────────
    
    @staticmethod
    def reply_start_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
        """Language selection menu for /start — 3 options with different colors."""
        builder = ReplyKeyboardBuilder()
        
        texts = {
            "uz": [
                ("🇺🇿 O'zbek", "primary"),       # Blue - primary action
                ("🇷🇺 Русский", "success"),      # Green - positive
                ("🇬🇧 English", "danger"),       # Red - different
            ],
            "ru": [
                ("🇺🇿 Узбекский", "primary"),
                ("🇷🇺 Русский", "success"),
                ("🇬🇧 Английский", "danger"),
            ],
            "en": [
                ("🇺🇿 Uzbek", "primary"),
                ("🇷🇺 Russian", "success"),
                ("🇬🇧 English", "danger"),
            ],
        }
        
        buttons_list = texts.get(lang, texts["uz"])
        
        for text, style in buttons_list:
            builder.add(StyledKeyboardButton(text=text, style=style))
        
        builder.adjust(1)  # 1 button per row
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def reply_main_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
        """Main menu for registered users — 5 buttons with mixed colors."""
        builder = ReplyKeyboardBuilder()
        
        # Color scheme for main menu:
        # Row 1: Profile (blue), Settings (green)
        # Row 2: Message Admin (red), Lessons (blue)
        # Row 3: Test (green)
        
        buttons_config = {
            "uz": [
                ("👤 Profil", "primary"),
                ("⚙️ Sozlamalar", "success"),
                ("📝 Admin ga xabar", "danger"),
                ("📚 Darslar", "primary"),
                ("✅ Test", "success"),
            ],
            "ru": [
                ("👤 Профиль", "primary"),
                ("⚙️ Настройки", "success"),
                ("📝 Написать админу", "danger"),
                ("📚 Уроки", "primary"),
                ("✅ Тест", "success"),
            ],
            "en": [
                ("👤 Profile", "primary"),
                ("⚙️ Settings", "success"),
                ("📝 Message admin", "danger"),
                ("📚 Lessons", "primary"),
                ("✅ Test", "success"),
            ],
        }
        
        buttons = buttons_config.get(lang, buttons_config["uz"])
        
        for text, style in buttons:
            builder.add(StyledKeyboardButton(text=text, style=style))
        
        builder.adjust(2, 2, 1)  # 2-2-1 layout
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def reply_settings_menu(lang: str = "uz") -> ReplyKeyboardMarkup:
        """Settings menu — reply keyboard matching settings_kb options.

        Buttons: Language change, AI ON/OFF, Log Out, Back.
        Texts must match @router.message handlers in menu.py.
        """
        builder = ReplyKeyboardBuilder()

        buttons = {
            "uz": [
                ("🌐 Til o'zgartirish", "primary"),
                ("🤖 AI ON/OFF", "success"),
                ("🚪 Log Out", "danger"),
                ("⬅️ Orqaga", "primary"),
            ],
            "ru": [
                ("🌐 Сменить язык", "primary"),
                ("🤖 AI ON/OFF", "success"),
                ("🚪 Выйти", "danger"),
                ("⬅️ Назад", "primary"),
            ],
            "en": [
                ("🌐 Change Language", "primary"),
                ("🤖 AI ON/OFF", "success"),
                ("🚪 Log Out", "danger"),
                ("⬅️ Back", "primary"),
            ],
        }

        button_list = buttons.get(lang, buttons["uz"])

        for text, style in button_list:
            builder.add(StyledKeyboardButton(text=text, style=style))

        builder.adjust(2, 1, 1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def reply_admin_massage(lang: str = "uz") -> ReplyKeyboardMarkup:
        """Admin contact session reply keyboard — Back button to exit session.

        User types their message naturally; presses Back to return to main menu.
        Text '⬅️ Orqaga' is caught by handle_admin_contact_session via MENU_BUTTONS.
        """
        builder = ReplyKeyboardBuilder()

        texts = {
            "uz": "⬅️ Orqaga",
            "ru": "⬅️ Назад",
            "en": "⬅️ Back",
        }

        text = texts.get(lang, texts["uz"])

        builder.add(StyledKeyboardButton(text=text, style="primary"))

        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def reply_contact(lang: str = "uz") -> ReplyKeyboardMarkup:
        """Phone sharing keyboard — green for positive action."""
        builder = ReplyKeyboardBuilder()
        
        texts = {
            "uz": "📞 Telefon raqamni ulashish",
            "ru": "📞 Поделиться номером",
            "en": "📞 Share Phone Number",
        }
        
        text = texts.get(lang, texts["uz"])
        
        builder.add(
            StyledKeyboardButton(
                text=text,
                request_contact=True,
                style="success"  # Green for positive action
            )
        )
        
        return builder.as_markup(resize_keyboard=True)
    
    # ─── INLINE KEYBOARDS ───────────────────────────────────────
    
    @staticmethod
    def inline_confirm(lang: str = "uz") -> InlineKeyboardMarkup:
        """Confirmation menu — Yes (green), No (red)."""
        builder = InlineKeyboardBuilder()
        
        texts = {
            "uz": {"yes": "✅ Ha", "no": "❌ Yo'q"},
            "ru": {"yes": "✅ Да", "no": "❌ Нет"},
            "en": {"yes": "✅ Yes", "no": "❌ No"},
        }
        
        items = texts.get(lang, texts["uz"])
        
        builder.add(
            StyledInlineKeyboardButton(text=items["yes"], callback_data="confirm_yes", style="success"),
            StyledInlineKeyboardButton(text=items["no"], callback_data="confirm_no", style="danger"),
        )
        
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def inline_navigation(lang: str = "uz", page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
        """Navigation menu — Previous (primary), Page (default), Next (primary)."""
        builder = InlineKeyboardBuilder()
        
        if page > 1:
            builder.add(
                StyledInlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page_{page-1}", style="primary")
            )
        
        builder.add(
            StyledInlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="noop")
        )
        
        if page < total_pages:
            builder.add(
                StyledInlineKeyboardButton(text="Keyingi ➡️", callback_data=f"page_{page+1}", style="primary")
            )
        
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def inline_settings_actions(lang: str = "uz") -> InlineKeyboardMarkup:
        """Settings action buttons — mixed colors."""
        builder = InlineKeyboardBuilder()
        
        texts = {
            "uz": [
                ("🔧 O'zgartirish", "edit_setting", "primary"),
                ("📊 Ko'rish", "view_setting", "success"),
                ("❌ O'chirish", "delete_setting", "danger"),
                ("⬅️ Orqaga", "back_to_menu", "primary"),
            ],
            "ru": [
                ("🔧 Изменить", "edit_setting", "primary"),
                ("📊 Просмотр", "view_setting", "success"),
                ("❌ Удалить", "delete_setting", "danger"),
                ("⬅️ Назад", "back_to_menu", "primary"),
            ],
            "en": [
                ("🔧 Edit", "edit_setting", "primary"),
                ("📊 View", "view_setting", "success"),
                ("❌ Delete", "delete_setting", "danger"),
                ("⬅️ Back", "back_to_menu", "primary"),
            ],
        }
        
        buttons = texts.get(lang, texts["uz"])
        
        for text, callback, style in buttons:
            builder.add(StyledInlineKeyboardButton(text=text, callback_data=callback, style=style))
        
        builder.adjust(2)
        return builder.as_markup()