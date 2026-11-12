"""Conversation context management for AI Teacher.

Provides functions to fetch and format conversation history from Backend API.
"""

from bot.utils.backend_http import BackendClient
from typing import List, Dict, Optional
from bot.config import settings


async def fetch_conversation_context(
    user_id: int,
    limit: int = 10,
    base_url: Optional[str] = None,
) -> List[Dict]:
    """
    Fetch last N messages from conversation history via Backend API.

    Args:
        user_id: Telegram user ID
        limit: Number of recent messages to fetch
        base_url: Backend API base URL (optional)

    Returns:
        List of message dicts with 'role' and 'content' keys
    """
    api_url = base_url or settings.API_BASE_URL
    import httpx

    try:
        async with BackendClient(timeout=5.0) as client:
            resp = await client.get(
                f"{api_url}/users/me/conversations?limit={limit}",
                headers={"X-Telegram-User-ID": str(user_id)},
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    return data.get("messages", [])
                return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[AI CONTEXT] Failed to fetch context: {e}")

    return []


def format_messages_for_ai(
    context: List[Dict],
    new_message: str,
    system_prompt: Optional[str] = None,
) -> List[Dict]:
    """
    Format conversation context + new message into OpenRouter API format.

    Args:
        context: List of {role, content} dicts from fetch_conversation_context
        new_message: Current user message
        system_prompt: Optional system prompt (prepended)

    Returns:
        List of messages ready for OpenRouter
    """
    messages = []

    # Add system prompt if provided
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Add context messages
    for msg in context:
        role = "assistant" if msg.get("role") == "assistant" else "user"
        content = msg.get("content", "")
        if content:
            messages.append({"role": role, "content": content})

    # Add current message
    messages.append({"role": "user", "content": new_message})

    return messages

