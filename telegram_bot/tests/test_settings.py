"""Tests for settings menu navigation, language change, AI toggle, and logout flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import bot modules
from bot.handlers.menu import (
    settings_language, back_to_settings, settings_logout, settings_ai_toggle,
    menu_settings, change_language,
)
from bot.keyboards.inline import settings_kb, language_switch_kb, main_menu_kb, settings_menu_kb
from bot.states.registration import MenuSection, RegisteredSection, StartSection


# ══════════════════════════════════════════════════════════════
# Settings Language Handler Tests
# ══════════════════════════════════════════════════════════════

class TestSettingsLanguage:
    """Test settings_language callback handler."""

    @pytest.mark.asyncio
    async def test_settings_language_sets_state(self, mock_callback, mock_state):
        """Settings language should set MenuSection.language_selection state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await settings_language(mock_callback, mock_state)

        mock_state.set_state.assert_called_once_with(MenuSection.language_selection)
        mock_callback.message.edit_text.assert_called_once()
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_settings_language_uses_language_switch_kb(self, mock_callback, mock_state):
        """Settings language should use language_switch_kb."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await settings_language(mock_callback, mock_state)

        call_kwargs = mock_callback.message.edit_text.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None


# ══════════════════════════════════════════════════════════════
# Back to Settings Handler Tests
# ══════════════════════════════════════════════════════════════

class TestBackToSettings:
    """Test back_to_settings callback handler."""

    @pytest.mark.asyncio
    async def test_back_to_settings_returns_to_settings(self, mock_callback, mock_state):
        """Back to settings should show settings menu."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await back_to_settings(mock_callback, mock_state)

        mock_callback.message.answer.assert_called_once()
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_back_to_settings_uses_settings_kb(self, mock_callback, mock_state):
        """Back to settings should use settings_kb."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await back_to_settings(mock_callback, mock_state)

        call_kwargs = mock_callback.message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None

    @pytest.mark.asyncio
    async def test_back_to_settings_uses_correct_language(self, mock_callback, mock_state):
        """Back to settings should use user's language."""
        mock_state.get_data = AsyncMock(return_value={"lang": "ru"})

        await back_to_settings(mock_callback, mock_state)

        call_args = mock_callback.message.answer.call_args
        assert "Настройки" in call_args.args[0]


# ══════════════════════════════════════════════════════════════
# Settings Logout Handler Tests
# ══════════════════════════════════════════════════════════════

class TestSettingsLogout:
    """Test settings_logout callback handler."""

    @pytest.mark.asyncio
    async def test_settings_logout_clears_state(self, mock_callback, mock_state):
        """Logout should clear FSM state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await settings_logout(mock_callback, mock_state)

        mock_state.clear.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_settings_logout_uses_inline_keyboard(self, mock_callback, mock_state):
        """Logout should show main menu with inline keyboard."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await settings_logout(mock_callback, mock_state)

        call_kwargs = mock_callback.message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None


# ══════════════════════════════════════════════════════════════
# Settings AI Toggle Handler Tests
# ══════════════════════════════════════════════════════════════

class TestSettingsAIToggle:
    """Test settings_ai_toggle callback handler."""

    @pytest.mark.asyncio
    async def test_settings_ai_toggle_enables_ai(self, mock_callback, mock_state, mock_httpx_client):
        """AI toggle should enable AI when currently disabled."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "ai_enabled": False,
            "telegram_id": 123456789,
        })

        await settings_ai_toggle(mock_callback, mock_state)

        # Verify state was updated
        mock_state.update_data.assert_called_once_with(ai_enabled=True)
        # Verify callback was answered
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_settings_ai_toggle_disables_ai(self, mock_callback, mock_state, mock_httpx_client):
        """AI toggle should disable AI when currently enabled."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "ai_enabled": True,
            "telegram_id": 123456789,
        })

        await settings_ai_toggle(mock_callback, mock_state)

        # Verify state was updated
        mock_state.update_data.assert_called_once_with(ai_enabled=False)
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_settings_ai_toggle_handles_backend_error(self, mock_callback, mock_state):
        """AI toggle should handle backend errors gracefully."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "ai_enabled": True,
            "telegram_id": 123456789,
        })

        # Mock httpx to raise exception
        with patch("httpx.AsyncClient", side_effect=Exception("Connection error")):
            await settings_ai_toggle(mock_callback, mock_state)

        # Verify state was NOT updated (reverted)
        mock_state.update_data.assert_not_called()
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_settings_ai_toggle_refreshes_settings_menu(self, mock_callback, mock_state, mock_httpx_client):
        """AI toggle should refresh settings menu."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "ai_enabled": True,
            "telegram_id": 123456789,
        })

        await settings_ai_toggle(mock_callback, mock_state)

        # Verify settings menu was refreshed
        mock_callback.message.answer.assert_called_once()
        call_kwargs = mock_callback.message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs


# ══════════════════════════════════════════════════════════════
# Menu Settings Callback Tests
# ══════════════════════════════════════════════════════════════

class TestMenuSettings:
    """Test menu_settings callback handler."""

    @pytest.mark.asyncio
    async def test_menu_settings_sets_state(self, mock_callback, mock_state):
        """Menu settings should set MenuSection.settings state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await menu_settings(mock_callback, mock_state)

        mock_state.set_state.assert_called_once_with(MenuSection.settings)
        mock_callback.message.answer.assert_called_once()
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_menu_settings_uses_settings_kb(self, mock_callback, mock_state):
        """Menu settings should use settings_kb."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await menu_settings(mock_callback, mock_state)

        call_kwargs = mock_callback.message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None


# ══════════════════════════════════════════════════════════════
# Language Switch Keyboard Tests
# ══════════════════════════════════════════════════════════════

class TestLanguageSwitchKeyboard:
    """Test language_switch_kb."""

    def test_language_switch_kb_has_back_to_settings(self):
        """Language switch should have back_to_settings button."""
        keyboard = language_switch_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "back_to_settings" in callbacks

    def test_language_switch_kb_has_all_languages(self):
        """Language switch should have all 3 languages."""
        keyboard = language_switch_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "lang_uz" in callbacks
        assert "lang_ru" in callbacks
        assert "lang_en" in callbacks

    def test_language_switch_kb_all_languages(self):
        """Language switch should work for all languages."""
        for lang in ["uz", "ru", "en"]:
            keyboard = language_switch_kb(lang)
            assert keyboard is not None
            callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
            assert "back_to_settings" in callbacks


# ══════════════════════════════════════════════════════════════
# Change Language Handler Tests
# ══════════════════════════════════════════════════════════════

class TestChangeLanguage:
    """Test change_language callback handler."""

    @pytest.mark.asyncio
    async def test_change_language_registered_user(self, mock_callback, mock_state):
        """Registered user changing language should go to RegisteredSection.main_menu."""
        mock_callback.data = "lang_ru"
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "registration_complete": True,
        })
        mock_state.get_state = AsyncMock(return_value="MenuSection:language_selection")

        await change_language(mock_callback, mock_state)

        # Verify state was updated with new language
        mock_state.update_data.assert_called_once_with(lang="ru")
        # Verify state was set to registered main menu
        mock_state.set_state.assert_called_once_with(RegisteredSection.main_menu)
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_language_non_registered_user(self, mock_callback, mock_state):
        """Non-registered user changing language should go to StartSection.main_menu."""
        mock_callback.data = "lang_en"
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "registration_complete": False,
        })
        mock_state.get_state = AsyncMock(return_value="MenuSection:language_selection")

        await change_language(mock_callback, mock_state)

        # Verify state was updated with new language
        mock_state.update_data.assert_called_once_with(lang="en")
        # Verify state was set to start main menu
        mock_state.set_state.assert_called_once_with(StartSection.main_menu)
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_language_uses_inline_keyboard(self, mock_callback, mock_state):
        """Change language should use inline keyboard."""
        mock_callback.data = "lang_uz"
        mock_state.get_data = AsyncMock(return_value={
            "lang": "ru",
            "registration_complete": True,
        })
        mock_state.get_state = AsyncMock(return_value="MenuSection:language_selection")

        await change_language(mock_callback, mock_state)

        # Verify reply_markup was passed in answer
        call_kwargs = mock_callback.message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None
