"""Tests for menu navigation and back button routing."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import bot modules
from bot.handlers.menu import back_to_menu, language_selected, msg_settings, cmd_about
from bot.keyboards.orange_keyboard import ColoredKeyboard
from bot.keyboards.inline import settings_kb, language_selection, about_us_kb
from bot.states.registration import (
    StartSection, RegisteredSection, MenuSection,
)


# ══════════════════════════════════════════════════════════════
# ColoredKeyboard Tests
# ══════════════════════════════════════════════════════════════

class TestColoredKeyboard:
    """Test ColoredKeyboard main menu layout."""

    def test_reply_main_menu_has_test_button(self):
        """Test button should be present in main menu."""
        keyboard = ColoredKeyboard.reply_main_menu("uz")
        buttons = [btn.text for row in keyboard.keyboard for btn in row]
        assert "✅ Test" in buttons

    def test_reply_main_menu_layout_2_2_1(self):
        """Main menu should have 2-2-1 layout (5 buttons)."""
        keyboard = ColoredKeyboard.reply_main_menu("uz")
        rows = keyboard.keyboard
        assert len(rows) == 3  # 3 rows
        assert len(rows[0]) == 2  # Row 1: 2 buttons
        assert len(rows[1]) == 2  # Row 2: 2 buttons
        assert len(rows[2]) == 1  # Row 3: 1 button

    def test_reply_main_menu_all_languages(self):
        """Main menu should work for all languages."""
        for lang in ["uz", "ru", "en"]:
            keyboard = ColoredKeyboard.reply_main_menu(lang)
            assert keyboard is not None
            assert len(keyboard.keyboard) == 3

    def test_reply_main_menu_has_profile_button(self):
        """Profile button should be present."""
        keyboard = ColoredKeyboard.reply_main_menu("uz")
        buttons = [btn.text for row in keyboard.keyboard for btn in row]
        assert "👤 Profil" in buttons

    def test_reply_main_menu_has_settings_button(self):
        """Settings button should be present."""
        keyboard = ColoredKeyboard.reply_main_menu("uz")
        buttons = [btn.text for row in keyboard.keyboard for btn in row]
        assert "⚙️ Sozlamalar" in buttons

    def test_reply_main_menu_has_admin_button(self):
        """Admin message button should be present."""
        keyboard = ColoredKeyboard.reply_main_menu("uz")
        buttons = [btn.text for row in keyboard.keyboard for btn in row]
        assert "📝 Admin ga xabar" in buttons

    def test_reply_main_menu_has_lessons_button(self):
        """Lessons button should be present."""
        keyboard = ColoredKeyboard.reply_main_menu("uz")
        buttons = [btn.text for row in keyboard.keyboard for btn in row]
        assert "📚 Darslar" in buttons


# ══════════════════════════════════════════════════════════════
# Back to Menu Handler Tests
# ══════════════════════════════════════════════════════════════

class TestBackToMenu:
    """Test back_to_menu callback handler."""

    @pytest.mark.asyncio
    async def test_back_to_menu_registered_user(self, mock_callback, mock_state):
        """Registered user should go to RegisteredSection.main_menu."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "registration_complete": True,
        })

        await back_to_menu(mock_callback, mock_state)

        # Verify state was set to registered main menu
        mock_state.set_state.assert_called_once_with(RegisteredSection.main_menu)
        # Verify message was edited with main menu
        mock_callback.message.edit_text.assert_called_once()
        # Verify callback was answered
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_back_to_menu_non_registered_user(self, mock_callback, mock_state):
        """Non-registered user should go to StartSection.main_menu."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "registration_complete": False,
        })

        await back_to_menu(mock_callback, mock_state)

        # Verify state was set to start main menu
        mock_state.set_state.assert_called_once_with(StartSection.main_menu)
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_back_to_menu_uses_colored_keyboard(self, mock_callback, mock_state):
        """Back to menu should use ColoredKeyboard."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "registration_complete": True,
        })

        await back_to_menu(mock_callback, mock_state)

        # Verify reply_markup was passed
        call_kwargs = mock_callback.message.edit_text.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None

    @pytest.mark.asyncio
    async def test_back_to_menu_uses_correct_language(self, mock_callback, mock_state):
        """Back to menu should use user's language."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "ru",
            "registration_complete": True,
        })

        await back_to_menu(mock_callback, mock_state)

        # Verify Russian text was used
        call_args = mock_callback.message.edit_text.call_args
        assert "Главное меню" in call_args.args[0] or "🏠" in call_args.args[0]


# ══════════════════════════════════════════════════════════════
# Settings Keyboard Tests
# ══════════════════════════════════════════════════════════════

class TestSettingsKeyboard:
    """Test settings keyboard navigation."""

    def test_settings_kb_back_button_uses_back_to_settings(self):
        """Settings back button should use back_to_settings callback."""
        keyboard = settings_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "back_to_settings" in callbacks
        assert "back_to_menu" not in callbacks

    def test_settings_kb_has_language_button(self):
        """Settings should have language button."""
        keyboard = settings_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "settings_language" in callbacks

    def test_settings_kb_has_ai_toggle(self):
        """Settings should have AI toggle button."""
        keyboard = settings_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "settings_ai_toggle" in callbacks

    def test_settings_kb_has_logout(self):
        """Settings should have logout button."""
        keyboard = settings_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "settings_logout" in callbacks

    def test_settings_kb_all_languages(self):
        """Settings keyboard should work for all languages."""
        for lang in ["uz", "ru", "en"]:
            keyboard = settings_kb(lang)
            assert keyboard is not None
            callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
            assert "back_to_settings" in callbacks


# ══════════════════════════════════════════════════════════════
# Language Selection Tests
# ══════════════════════════════════════════════════════════════

class TestLanguageSelection:
    """Test language selection keyboard."""

    def test_language_selection_has_back_button(self):
        """Language selection with include_back should have back_to_menu."""
        keyboard = language_selection(include_back=True)
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "back_to_menu" in callbacks

    def test_language_selection_without_back(self):
        """Language selection without include_back should not have back button."""
        keyboard = language_selection(include_back=False)
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "back_to_menu" not in callbacks

    def test_language_selection_has_all_languages(self):
        """Language selection should have all 3 languages."""
        keyboard = language_selection()
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "lang_uz" in callbacks
        assert "lang_ru" in callbacks
        assert "lang_en" in callbacks


# ══════════════════════════════════════════════════════════════
# About Us Tests
# ══════════════════════════════════════════════════════════════

class TestAboutUs:
    """Test about us keyboard."""

    def test_about_us_kb_has_back_button(self):
        """About us should have back_to_menu button."""
        keyboard = about_us_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "back_to_menu" in callbacks

    def test_about_us_kb_has_website_link(self):
        """About us should have website link."""
        keyboard = about_us_kb("uz")
        urls = [btn.url for row in keyboard.inline_keyboard for btn in row if btn.url]
        assert "https://myestro.uz" in urls


# ══════════════════════════════════════════════════════════════
# Settings Message Handler Tests
# ══════════════════════════════════════════════════════════════

class TestSettingsHandler:
    """Test settings message handler."""

    @pytest.mark.asyncio
    async def test_msg_settings_sets_state(self, mock_message, mock_state):
        """Settings handler should set MenuSection.settings state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await msg_settings(mock_message, mock_state)

        mock_state.set_state.assert_called_once_with(MenuSection.settings)
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_msg_settings_uses_settings_kb(self, mock_message, mock_state):
        """Settings handler should use settings_kb."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await msg_settings(mock_message, mock_state)

        call_kwargs = mock_message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None


# ══════════════════════════════════════════════════════════════
# About Handler Tests
# ══════════════════════════════════════════════════════════════

class TestAboutHandler:
    """Test about us message handler."""

    @pytest.mark.asyncio
    async def test_cmd_about_sets_state(self, mock_message, mock_state):
        """About handler should set MenuSection.about_us state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await cmd_about(mock_message, mock_state)

        mock_state.set_state.assert_called_once_with(MenuSection.about_us)
        mock_message.answer.assert_called_once()