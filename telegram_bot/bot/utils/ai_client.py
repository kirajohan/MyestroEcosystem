"""Re-export shared AI client for bot compatibility."""
from shared.ai_client import (
    build_teacher_prompt,
    FALLBACK_MODELS,
    shutdown_ai_client,
    WHISPER_SERVICE_URL,
    stream_ask_ai as _shared_stream_ask_ai,
)
from bot.config import settings


async def ask_ai(
    prompt: str,
    chat_history=None,
    system_prompt=None,
    model=None,
    temperature=0.7,
    max_tokens=1024,
) -> str:
    """Wrapper: calls shared ask_ai with bot's OpenRouter credentials."""
    from shared.ai_client import ask_ai as _shared_ask_ai
    return await _shared_ask_ai(
        prompt=prompt,
        chat_history=chat_history,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        openrouter_base_url=settings.OPENROUTER_BASE_URL,
        openrouter_api_key=settings.OPENROUTER_API_KEY,
    )


async def stream_ask_ai(
    prompt: str,
    chat_history=None,
    system_prompt=None,
    model=None,
    temperature=0.7,
    max_tokens=1024,
):
    """Wrapper: calls shared stream_ask_ai with bot's OpenRouter credentials."""
    async for chunk in _shared_stream_ask_ai(
        prompt=prompt,
        chat_history=chat_history,
        system_prompt=system_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        openrouter_base_url=settings.OPENROUTER_BASE_URL,
        openrouter_api_key=settings.OPENROUTER_API_KEY,
    ):
        yield chunk


async def transcribe_voice(audio_bytes: bytes) -> str:
    """Wrapper: calls shared transcribe_voice with bot's credentials."""
    from shared.ai_client import transcribe_voice as _shared_transcribe
    return await _shared_transcribe(
        audio_bytes,
        openrouter_base_url=settings.OPENROUTER_BASE_URL,
        openrouter_api_key=settings.OPENROUTER_API_KEY,
    )


async def transcribe_voice_via_service(
    audio_bytes: bytes,
    *,
    base_url: str = WHISPER_SERVICE_URL,
    language: str = "uz",
    timeout: float = 30.0,
) -> str:
    """Wrapper: calls shared transcribe_voice_via_service."""
    from shared.ai_client import transcribe_voice_via_service as _shared_transcribe_service
    return await _shared_transcribe_service(
        audio_bytes,
        base_url=base_url,
        language=language,
        timeout=timeout,
    )

