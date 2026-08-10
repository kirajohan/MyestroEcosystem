"""AI service — re-exports shared client and adds backend-specific features."""
'''C:\Projects\MyestroEco\MyestroEco\telegram_bot\backend\app\services\ai_service.py'''

import json
import logging
from typing import List, Dict, Any

from shared.ai_client import (
    ask_ai as _shared_ask_ai,
    shutdown_ai_client,
    get_ai_client,
    FALLBACK_MODELS,
)
from app.config import settings

logger = logging.getLogger(__name__)

# Backend-specific wrapper with auto-injected config
async def ask_ai(
    prompt: str,
    chat_history=None,
    system_prompt=None,
    model=None,
    temperature=0.7,
    max_tokens=1024,
) -> str:
    """Wrapper: calls shared ask_ai with backend's OpenRouter credentials."""
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


async def analyze_error_logs(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze error logs using AI to suggest causes and solutions.
    
    Returns a list of dicts with keys: error_type, cause, solution.
    Uses improved prompt with JSON schema to guarantee parseable output.
    """
    if not logs:
        return []

    log_text = "\n".join([
        f"- Error: {log.get('error_type', 'Unknown')} | Message: {log.get('error_message', '')} | Service: {log.get('service', 'unknown')}"
        for log in logs[:10]
    ])

    system_prompt = """You are a senior DevOps engineer analyzing error logs.
You MUST return ONLY a valid JSON array. No markdown, no code blocks, no explanation.
Each object in the array must have exactly these fields:
- "error_type": string
- "cause": string (root cause analysis)
- "solution": string (actionable fix)

Example:
[{"error_type": "DatabaseConnectionError", "cause": "Connection pool exhausted", "solution": "Increase pool_size in database config"}]

If you cannot determine cause/solution, use "Unknown" for cause and "Manual review needed" for solution."""

    prompt = f"""Analyze these error logs and return a JSON array with cause and solution for each:

{log_text}"""

    # First attempt
    result = await _shared_ask_ai(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=2048,
        openrouter_base_url=settings.OPENROUTER_BASE_URL,
        openrouter_api_key=settings.OPENROUTER_API_KEY,
    )

    parsed = _safe_parse_json(result)
    if parsed is not None:
        return parsed

    # Retry once with stricter instruction
    logger.warning("First AI JSON parse failed, retrying with stricter prompt...")
    retry_prompt = f"""The previous response was not valid JSON. Return ONLY a valid JSON array for these logs:
{log_text}

Format: [{{"error_type": "...", "cause": "...", "solution": "..."}}]
No explanations, no markdown, just the JSON array."""

    result2 = await _shared_ask_ai(
        prompt=retry_prompt,
        temperature=0.1,
        max_tokens=2048,
        openrouter_base_url=settings.OPENROUTER_BASE_URL,
        openrouter_api_key=settings.OPENROUTER_API_KEY,
    )

    parsed = _safe_parse_json(result2)
    if parsed is not None:
        return parsed

    # Final fallback — return raw text wrapped in parse_failed
    logger.error("AI analyze_error_logs: failed to parse JSON after retry")
    return [{"error_type": "parse_failed", "cause": result, "solution": "Manual review needed"}]


def _safe_parse_json(text: str) -> list | None:
    """Attempt to parse JSON from AI response, handling markdown fences."""
    if not text:
        return None

    text = text.strip()
    # Remove markdown code block fences if present
    if text.startswith("```"):
        # Remove opening ```json or ``` and closing ```
        lines = text.splitlines()
        # Remove first and last lines if they are fences
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        # If it's a dict with a results/data key
        if isinstance(data, dict):
            for key in ("results", "data", "errors", "logs"):
                if key in data and isinstance(data[key], list):
                    return data[key]
    except json.JSONDecodeError:
        pass

    return None


async def health_check() -> dict:
    """Check OpenRouter API health using shared client."""
    try:
        client = get_ai_client()
        resp = await client.get(
            f"{settings.OPENROUTER_BASE_URL}/models",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            timeout=10.0,
        )
        if resp.status_code == 200:
            return {"status": "ok", "models_available": len(resp.json().get("data", []))}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    return {"status": "error", "detail": "Unknown error"}