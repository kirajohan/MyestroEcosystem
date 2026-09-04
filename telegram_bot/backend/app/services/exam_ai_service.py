"""
AI Evaluation Service for Writing & Speaking.
OpenRouter API orqali ishlaydi — Fallback tizimi bilan.
Telegram bot'dagi kabi bir nechta modellarni sinab ko'radi.
"""

import json
import logging
import os
from typing import Optional, Dict, Any, List

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ═══════════════════════════════════════════════════════════
# FALLBACK MODELS — Telegram bot'dagi kabi ketma-ket sinab ko'riladi
# ═══════════════════════════════════════════════════════════
FALLBACK_MODELS: List[str] = [
    "openai/gpt-4o-mini",                         # ✅ Ishlagan, arzon ($0.15/1M tokens)
    "meta-llama/llama-3.3-70b-instruct:free",     # ✅ Free tier
    "qwen/qwen-2.5-72b-instruct:free",            # ✅ Free tier
    "deepseek/deepseek-chat",                     # ✅ Juda arzon ($0.14/1M tokens)
    "mistralai/mistral-7b-instruct:free",         # ✅ Free tier
]


async def _call_openrouter(
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout: float = 60.0,
) -> Dict[str, Any]:
    """Bitta model bilan OpenRouter'ga so'rov yuboradi."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://myestro.uz",
                "X-Title": "Myestro Exam AI",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
        )

        if response.status_code != 200:
            error_text = response.text[:200]
            logger.warning(f"⚠️ Model {model} failed: {response.status_code} - {error_text}")
            raise ValueError(f"HTTP {response.status_code}: {error_text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # JSON parse qilish
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Model {model} returned invalid JSON: {e}")
            raise ValueError(f"Invalid JSON from {model}")

        return result


async def evaluate_writing(
    task_instruction: str,
    student_text: str,
    cefr_level: str,
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Writing matnini AI orqali baholaydi.
    Fallback tizimi — agar birinchi model ishlamasa, keyingisini sinaydi.
    """
    if not OPENROUTER_API_KEY:
        logger.error("❌ OPENROUTER_API_KEY not set!")
        return {"error": "API key not configured", "overall_score": 0}

    # System prompt tayyorlash
    if not system_prompt:
        system_prompt = f"""You are an expert English language examiner specializing in CEFR assessment.

Evaluate the student's writing based on CEFR {cefr_level} criteria.

TASK: {task_instruction}
{"MIN WORDS: " + str(min_words) if min_words else ""}
{"MAX WORDS: " + str(max_words) if max_words else ""}

You MUST respond with ONLY valid JSON (no markdown, no explanation, no code blocks):
{{
  "overall_score": <0-100 integer>,
  "cefr_estimate": "<A1|A2|B1|B2|C1|C2>",
  "criteria": [
    {{
      "name": "Task Achievement",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment>"
    }},
    {{
      "name": "Coherence & Cohesion",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment>"
    }},
    {{
      "name": "Lexical Resource",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment>"
    }},
    {{
      "name": "Grammar Range & Accuracy",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment>"
    }}
  ],
  "corrections": [
    {{
      "original": "<wrong sentence>",
      "corrected": "<corrected sentence>",
      "explanation": "<why>"
    }}
  ],
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "recommendations": ["<tip 1>", "<tip 2>"]
}}"""

    user_prompt = f"Evaluate this writing:\n\n{student_text}"

    # ═══════════════════════════════════════════════════════
    # FALLBACK LOOP — har bir modelni sinab ko'ramiz
    # ═══════════════════════════════════════════════════════
    last_error = None

    for model in FALLBACK_MODELS:
        try:
            logger.info(f"🤖 Trying model: {model}")
            result = await _call_openrouter(model, system_prompt, user_prompt)

            # Validatsiya
            if "overall_score" not in result:
                result["overall_score"] = 0
            if "criteria" not in result:
                result["criteria"] = []

            result["model_used"] = model
            logger.info(f"✅ Success with {model}: score={result.get('overall_score')}")
            return result

        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ Model {model} failed: {e}")
            continue

    # Barcha modellar muvaffaqiyatsiz
    logger.error(f"❌ All {len(FALLBACK_MODELS)} models failed. Last error: {last_error}")
    return {
        "error": f"All models failed. Last: {last_error}",
        "overall_score": 0,
        "criteria": [],
        "model_used": None,
    }