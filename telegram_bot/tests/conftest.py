"""Pytest configuration and shared fixtures for Telegram bot tests."""

import os
import sys
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Add bot directory to path for imports
_bot_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bot"))
if _bot_root not in sys.path:
    sys.path.insert(0, _bot_root)

# Add telegram_bot root to path
_telegram_bot_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _telegram_bot_root not in sys.path:
    sys.path.insert(0, _telegram_bot_root)

# Set test environment variables before importing bot modules
os.environ.setdefault("BOT_TOKEN", "test_token_123456789")
os.environ.setdefault("API_BASE_URL", "http://test-backend:8002")
os.environ.setdefault("BACKEND_URL", "http://test-backend:8002")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("CHANNEL_ID", "")
os.environ.setdefault("CHANNEL_USERNAME", "")
os.environ.setdefault("CHANNEL_URL", "")
os.environ.setdefault("OPENROUTER_API_KEY", "test_key")
os.environ.setdefault("ADMIN_IDS", "123456789")


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_state():
    """Create a mock FSMContext with common methods."""
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "lang": "uz",
        "registration_complete": True,
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+998901234567",
        "cefr_level": "A1",
        "telegram_id": 123456789,
        "id": 1,
    })
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    state.get_state = AsyncMock(return_value="RegisteredSection:main_menu")
    state.clear = AsyncMock()
    return state


@pytest.fixture
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 123456789
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.from_user.full_name = "Test User"
    message.from_user.username = "testuser"
    message.text = "Test message"
    message.caption = None
    message.content_type = "text"
    message.chat = MagicMock()
    message.chat.type = "private"
    message.answer = AsyncMock()
    message.edit_text = AsyncMock()
    message.edit_reply_markup = AsyncMock()
    message.answer_video = AsyncMock()
    message.answer_document = AsyncMock()
    message.forward_origin = None
    message.contact = None
    message.photo = None
    message.voice = None
    message.document = None
    message.video = None
    message.sticker = None
    return message


@pytest.fixture
def mock_callback():
    """Create a mock CallbackQuery object."""
    callback = AsyncMock()
    callback.from_user = MagicMock()
    callback.from_user.id = 123456789
    callback.from_user.first_name = "Test"
    callback.from_user.full_name = "Test User"
    callback.from_user.username = "testuser"
    callback.data = "back_to_menu"
    callback.message = AsyncMock()
    callback.message.edit_text = AsyncMock()
    callback.message.answer = AsyncMock()
    callback.message.edit_reply_markup = AsyncMock()
    callback.answer = AsyncMock()
    return callback


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient to avoid real API calls."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"exists": False, "user": {}}

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.put = AsyncMock(return_value=mock_response)

    # Support async context manager: async with httpx.AsyncClient() as client
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client) as mock:
        yield mock
