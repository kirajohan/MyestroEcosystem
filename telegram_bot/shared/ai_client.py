"""Shared AI client with connection pooling for both bot and backend."""

import json
import httpx
import logging
from typing import Optional, List, Dict, AsyncGenerator, Union

logger = logging.getLogger(__name__)

FALLBACK_MODELS = [
    "google/gemini-2.0-flash-lite-preview-02-05",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "mistralai/mistral-7b-instruct:free",
    "openai/gpt-4o-mini",
]

# Global client — lazy initialized for connection pooling
_client: Optional[httpx.AsyncClient] = None


def get_ai_client() -> httpx.AsyncClient:
    """Return global httpx AsyncClient (lazy init)."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=60.0)
    return _client


async def shutdown_ai_client():
    """Close global httpx client gracefully."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("AI HTTP client closed.")


def _build_messages(
    prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Build messages list for OpenRouter API."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": prompt})
    return messages


async def ask_ai(
    prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    *,
    openrouter_base_url: str,
    openrouter_api_key: str,
    stream: bool = False,
) -> Union[str, AsyncGenerator[str, None]]:
    """Send prompt to OpenRouter with fallback models and connection pooling.

    If stream=True, returns an async generator that yields text chunks.
    If stream=False (default), returns the full response string.
    """
    messages = _build_messages(prompt, chat_history, system_prompt)
    models_to_try = [model] if model else FALLBACK_MODELS
    client = get_ai_client()

    if stream:
        return _ask_ai_stream(
            messages=messages,
            models_to_try=models_to_try,
            client=client,
            openrouter_base_url=openrouter_base_url,
            openrouter_api_key=openrouter_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    for m in models_to_try:
        try:
            resp = await client.post(
                f"{openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": m,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.warning(f"Model {m} failed: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Model {m} error: {e}")

    logger.error("All AI models failed — returning fallback message")
    return "Hozirda texnik ishlar ketyapti. Iltimos, birozdan so'ng qayta urining."


async def _ask_ai_stream(
    messages: List[Dict[str, str]],
    models_to_try: List[str],
    client: httpx.AsyncClient,
    openrouter_base_url: str,
    openrouter_api_key: str,
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    """Internal streaming helper used by ask_ai(stream=True) and stream_ask_ai()."""
    for m in models_to_try:
        try:
            async with client.stream(
                "POST",
                f"{openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": m,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                timeout=httpx.Timeout(60.0, connect=10.0),
            ) as resp:
                if resp.status_code != 200:
                    logger.warning(f"Streaming model {m} failed: {resp.status_code}")
                    continue

                async for raw_line in resp.aiter_lines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        return
                    try:
                        payload = json.loads(data)
                        delta = payload["choices"][0]["delta"]
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.debug(f"SSE parse skipped: {e}")
                        continue
            return
        except Exception as e:
            logger.warning(f"Streaming model {m} error: {e}")
            continue

    logger.error("All streaming models failed (_ask_ai_stream) — returning fallback message")
    yield "Hozirda texnik ishlar ketyapti. Iltimos, birozdan so'ng qayta urining."


async def stream_ask_ai(
    prompt: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    *,
    openrouter_base_url: str,
    openrouter_api_key: str,
) -> AsyncGenerator[str, None]:
    """Stream AI response chunks from OpenRouter via SSE.

    Yields text chunks as they arrive. Handles fallback models if the first
    model fails with a streaming-compatible error.
    """
    messages = _build_messages(prompt, chat_history, system_prompt)
    models_to_try = [model] if model else FALLBACK_MODELS
    client = get_ai_client()

    for m in models_to_try:
        try:
            async with client.stream(
                "POST",
                f"{openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": m,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                timeout=httpx.Timeout(60.0, connect=10.0),
            ) as resp:
                if resp.status_code != 200:
                    logger.warning(f"Streaming model {m} failed: {resp.status_code}")
                    continue

                buffer = ""
                async for raw_line in resp.aiter_lines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        return
                    try:
                        payload = json.loads(data)
                        delta = payload["choices"][0]["delta"]
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError) as e:
                        logger.debug(f"SSE parse skipped: {e}")
                        continue
            return
        except Exception as e:
            logger.warning(f"Streaming model {m} error: {e}")
            continue

    logger.error("All streaming models failed (stream_ask_ai) — returning fallback message")
    yield "Hozirda texnik ishlar ketyapti. Iltimos, birozdan so'ng qayta urining."


def build_teacher_prompt(cefr_level: str, lang: str = "uz") -> str:
    """Build system prompt for AI teacher mode."""
    return f"""You are Myestro AI English teacher. Respond in {lang} language.
Student CEFR level: {cefr_level}.
- Adapt your vocabulary and grammar complexity to the student's level
- Correct mistakes gently
- Encourage practice
- Use examples from daily life
Keep responses concise (max 150 words)."""



