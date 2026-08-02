"""Tests for admin message flow and session state management."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import bot modules
from bot.handlers.menu import (
    cmd_admin_message, menu_registered_admin, handle_admin_contact_session,
)
from bot.keyboards.inline import admin_contact_kb
from bot.states.registration import MenuSection


# ══════════════════════════════════════════════════════════════
# Admin Contact Keyboard Tests
# ══════════════════════════════════════════════════════════════

class TestAdminContactKeyboard:
    """Test admin contact keyboard."""

    def test_admin_contact_kb_has_back_button(self):
        """Admin contact keyboard should have back_to_menu button."""
        keyboard = admin_contact_kb("uz")
        callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
        assert "back_to_menu" in callbacks

    def test_admin_contact_kb_all_languages(self):
        """Admin contact keyboard should work for all languages."""
        for lang in ["uz", "ru", "en"]:
            keyboard = admin_contact_kb(lang)
            assert keyboard is not None
            callbacks = [btn.callback_data for row in keyboard.inline_keyboard for btn in row]
            assert "back_to_menu" in callbacks


# ══════════════════════════════════════════════════════════════
# Admin Message Handler Tests
# ══════════════════════════════════════════════════════════════

class TestCmdAdminMessage:
    """Test cmd_admin_message handler."""

    @pytest.mark.asyncio
    async def test_cmd_admin_message_sets_state(self, mock_message, mock_state):
        """Admin message handler should set MenuSection.contact_admin state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await cmd_admin_message(mock_message, mock_state)

        mock_state.set_state.assert_called_once_with(MenuSection.contact_admin)
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_cmd_admin_message_uses_admin_contact_kb(self, mock_message, mock_state):
        """Admin message handler should use admin_contact_kb."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await cmd_admin_message(mock_message, mock_state)

        call_kwargs = mock_message.answer.call_args.kwargs
        assert "reply_markup" in call_kwargs
        assert call_kwargs["reply_markup"] is not None

    @pytest.mark.asyncio
    async def test_cmd_admin_message_uses_correct_language(self, mock_message, mock_state):
        """Admin message handler should use user's language."""
        mock_state.get_data = AsyncMock(return_value={"lang": "ru"})

        await cmd_admin_message(mock_message, mock_state)

        call_args = mock_message.answer.call_args
        assert "Связь с администратором" in call_args.args[0]


class TestMenuRegisteredAdmin:
    """Test menu_registered_admin callback handler."""

    @pytest.mark.asyncio
    async def test_menu_registered_admin_sets_state(self, mock_callback, mock_state):
        """Registered admin callback should set MenuSection.contact_admin state."""
        mock_state.get_data = AsyncMock(return_value={"lang": "uz"})

        await menu_registered_admin(mock_callback, mock_state)

        mock_state.set_state.assert_called_once_with(MenuSection.contact_admin)
        mock_callback.message.answer.assert_called_once()
        mock_callback.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_menu_registered_admin_uses_correct_language(self, mock_callback, mock_state):
        """Registered admin callback should use user's language."""
        mock_state.get_data = AsyncMock(return_value={"lang": "en"})

        await menu_registered_admin(mock_callback, mock_state)

        call_args = mock_callback.message.answer.call_args
        assert "Contact Administrator" in call_args.args[0]


# ══════════════════════════════════════════════════════════════
# Admin Contact Session Tests
# ══════════════════════════════════════════════════════════════

class TestAdminContactSession:
    """Test handle_admin_contact_session handler."""

    @pytest.mark.asyncio
    async def test_admin_contact_session_saves_message(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should save message to backend."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = "Hello admin, I need help"
        mock_message.content_type = "text"

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify backend was called
        mock_httpx_client.return_value.post.assert_called_once()
        # Verify user got response
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_contact_session_handles_backend_error(self, mock_message, mock_state):
        """Admin contact session should handle backend errors gracefully."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = "Hello admin"
        mock_message.content_type = "text"

        # Mock httpx to raise exception
        with patch("httpx.AsyncClient", side_effect=Exception("Connection error")):
            await handle_admin_contact_session(mock_message, mock_state)

        # Verify user still got a response
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_contact_session_uses_user_id(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should use user's telegram_id."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = "Test message"
        mock_message.content_type = "text"

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify payload includes user_telegram_id
        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert payload.get("user_telegram_id") == 123456789
        assert payload.get("user_id") == 1

    @pytest.mark.asyncio
    async def test_admin_contact_session_handles_photo(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should handle photo messages."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = None
        mock_message.caption = "Photo caption"
        mock_message.content_type = "photo"
        mock_message.photo = [MagicMock(file_id="photo_file_id_123")]

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify payload includes file_id
        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert payload.get("file_id") == "photo_file_id_123"
        assert payload.get("content_type") == "photo"

    @pytest.mark.asyncio
    async def test_admin_contact_session_handles_voice(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should handle voice messages."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = None
        mock_message.caption = None
        mock_message.content_type = "voice"
        mock_message.voice = MagicMock(file_id="voice_file_id_123")

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify payload includes file_id
        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert payload.get("file_id") == "voice_file_id_123"
        assert payload.get("content_type") == "voice"

    @pytest.mark.asyncio
    async def test_admin_contact_session_handles_document(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should handle document messages."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = None
        mock_message.caption = "Document caption"
        mock_message.content_type = "document"
        mock_message.document = MagicMock(file_id="doc_file_id_123")

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify payload includes file_id
        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert payload.get("file_id") == "doc_file_id_123"
        assert payload.get("content_type") == "document"

    @pytest.mark.asyncio
    async def test_admin_contact_session_handles_video(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should handle video messages."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = None
        mock_message.caption = "Video caption"
        mock_message.content_type = "video"
        mock_message.video = MagicMock(file_id="video_file_id_123")

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify payload includes file_id
        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert payload.get("file_id") == "video_file_id_123"
        assert payload.get("content_type") == "video"

    @pytest.mark.asyncio
    async def test_admin_contact_session_handles_sticker(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should handle sticker messages."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = None
        mock_message.caption = None
        mock_message.content_type = "sticker"
        mock_message.sticker = MagicMock(file_id="sticker_file_id_123")

        await handle_admin_contact_session(mock_message, mock_state)

        # Verify payload includes file_id
        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert payload.get("file_id") == "sticker_file_id_123"
        assert payload.get("content_type") == "sticker"

    @pytest.mark.asyncio
    async def test_admin_contact_session_uses_username(self, mock_message, mock_state, mock_httpx_client):
        """Admin contact session should include username in user_name."""
        mock_state.get_data = AsyncMock(return_value={
            "lang": "uz",
            "id": 1,
        })
        mock_message.text = "Test"
        mock_message.content_type = "text"

        await handle_admin_contact_session(mock_message, mock_state)

        call_args = mock_httpx_client.return_value.post.call_args
        payload = call_args.kwargs.get("json", {})
        assert "Test User" in payload.get("user_name", "")
        assert "@testuser" in payload.get("user_name", "")