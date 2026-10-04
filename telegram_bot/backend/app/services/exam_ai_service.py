"""
AI Evaluation Service for Writing & Speaking.
OpenRouter API orqali ishlaydi — Fallback tizimi bilan.
"""

import asyncio
import json
import logging
import os
from typing import Optional, Dict, Any, List

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ═══════════════════════════════════════════════════════════
# FALLBACK MODELS — Faqat ishonchli modellar
# ═══════════════════════════════════════════════════════════
FALLBACK_MODELS: List[str] = [
    "openai/gpt-4o-mini",                         # ✅ Asosiy — tez, arzon
    "google/gemini-2.0-flash-001",                # ✅ Zaxira 1
    "anthropic/claude-3.5-sonnet",                # ✅ Zaxira 2
    "meta-llama/llama-3.3-70b-instruct",          # ✅ Zaxira 3
]


def _model_attempts() -> List[str]:
    """Vaqtinchalik xatolar (429/timeout) uchun ro'yxatni 2 marta aylanadi."""
    return FALLBACK_MODELS + FALLBACK_MODELS


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
                "temperature": 0.2,  # Kamroq randomness
                "response_format": {"type": "json_object"},
            },
        )

        if response.status_code != 200:
            error_text = response.text[:200]
            logger.warning(f"⚠️ Model {model} failed: {response.status_code} - {error_text}")
            raise ValueError(f"HTTP {response.status_code}: {error_text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            text = (content or "").strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:]
            result = json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Model {model} returned invalid JSON: {e}")
            raise ValueError(f"Invalid JSON from {model}")

        return result


def _validate_writing_input(student_text: str, min_words: Optional[int]) -> Dict[str, Any]:
    """
    Writing matnini AI'ga yuborishdan oldin tekshirish.
    """
    if not student_text or not student_text.strip():
        return {
            "valid": False,
            "score": 0,
            "reason": "No text provided"
        }
    
    word_count = len(student_text.strip().split())
    
    # Minimal word count tekshiruvi
    effective_min = min_words if min_words and min_words > 0 else 20
    
    if word_count < effective_min:
        return {
            "valid": False,
            "score": 0,
            "reason": f"Too short: {word_count} words (minimum {effective_min} required)",
            "word_count": word_count
        }
    
    return {
        "valid": True,
        "word_count": word_count
    }


async def evaluate_writing(
    task_instruction: str,
    student_text: str,
    cefr_level: str,
    min_words: Optional[int] = None,
    max_words: Optional[int] = None,
    max_score: float = 100.0,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Writing matnini AI orqali baholaydi.
    
    Args:
        max_score: Maksimal ball (item.max_score dan keladi, odatda 1-10)
    """
    if not OPENROUTER_API_KEY:
        logger.error("❌ OPENROUTER_API_KEY not set!")
        return {"error": "API key not configured", "overall_score": 0}

    # ═══════════════════════════════════════════════════════
    # PRE-VALIDATION: AI'ga yuborishdan oldin tekshirish
    # ═══════════════════════════════════════════════════════
    validation = _validate_writing_input(student_text, min_words)
    
    if not validation["valid"]:
        logger.warning(f"⚠️ Writing validation failed: {validation['reason']}")
        return {
            "overall_score": 0,
            "cefr_estimate": "A1",
            "criteria": [
                {
                    "name": "Task Completion",
                    "score": 0,
                    "max_score": 10,
                    "comment": validation["reason"]
                }
            ],
            "corrections": [],
            "strengths": [],
            "weaknesses": [validation["reason"]],
            "recommendations": ["Write more content to meet the minimum requirement"],
            "model_used": "validation",
            "validation_failed": True
        }

    # System prompt tayyorlash
    if not system_prompt:
        system_prompt = f"""You are a strict English language examiner specializing in CEFR assessment.

CRITICAL RULES:
1. The response MUST be written in English. If it's in another language (like Uzbek, Russian, etc.), give 0 points.
2. The response must meet the minimum word requirement: {min_words or 20} words minimum.
3. Be STRICT and REALISTIC in scoring. Don't give high scores for poor quality.
4. If the text is too short, off-topic, or not in English, give very low scores (0-20 range).

Evaluate based on CEFR {cefr_level} criteria.

TASK: {task_instruction}
MINIMUM WORDS: {min_words or 20}
{"MAXIMUM WORDS: " + str(max_words) if max_words else "No maximum"}

SCORING SCALE:
- 0-20: Very poor (wrong language, too short, completely off-topic)
- 21-40: Poor (many errors, hard to understand)
- 41-60: Fair (some errors, basic communication)
- 61-80: Good (few errors, clear communication)
- 81-100: Excellent (native-like quality)

You MUST respond with ONLY valid JSON (no markdown, no explanation):
{{
  "overall_score": <0-100 integer, BE STRICT>,
  "cefr_estimate": "<A1|A2|B1|B2|C1|C2>",
  "criteria": [
    {{
      "name": "Task Achievement",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment>"
    }},
    {{
      "name": "Language (Must be English)",
      "score": <0-10, 0 if not English>,
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
  "strengths": ["<strength 1>"],
  "weaknesses": ["<weakness 1>"],
  "recommendations": ["<tip 1>"]
}}"""

    user_prompt = f"Student's writing ({validation['word_count']} words):\n\n{student_text}"

    # ═══════════════════════════════════════════════════════
    # FALLBACK LOOP
    # ═══════════════════════════════════════════════════════
    last_error = None

    for model in _model_attempts():
        try:
            logger.info(f"🤖 Trying model: {model}")
            result = await _call_openrouter(model, system_prompt, user_prompt)

            # Validatsiya
            if "overall_score" not in result:
                result["overall_score"] = 0
            if "criteria" not in result:
                result["criteria"] = []

            # ═══════════════════════════════════════════════════════
            # SCORE NORMALIZATION: AI 0-100 qaytaradi, lekin item max_score boshqa
            # Masalan: AI 74 qaytardi, lekin item max_score = 1
            # Normalize: 74/100 * 1 = 0.74
            # ═══════════════════════════════════════════════════════
            ai_score_100 = result.get("overall_score", 0)
            
            # Normalize to max_score
            normalized_score = (ai_score_100 / 100.0) * max_score
            result["overall_score_normalized"] = round(normalized_score, 2)
            result["overall_score_100"] = ai_score_100  # Original 0-100 score
            
            result["model_used"] = model
            logger.info(f"✅ Success with {model}: score={ai_score_100}/100 → {normalized_score:.2f}/{max_score}")
            return result

        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ Model {model} failed: {e}")
            await asyncio.sleep(1.5)
            continue

    # Barcha modellar muvaffaqiyatsiz
    logger.error(f"❌ All {len(FALLBACK_MODELS)} models failed. Last error: {last_error}")
    return {
        "error": f"All models failed. Last: {last_error}",
        "overall_score": 0,
        "overall_score_normalized": 0,
        "criteria": [],
        "model_used": None,
    }

# app/services/exam_ai_service.py faylining oxiriga qo'shing

async def evaluate_speaking(
    task_instruction: str,
    transcript_text: str,
    cefr_level: str,
    duration_sec: Optional[int] = None,
    max_score: float = 100.0,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Speaking (gapirish) javobini AI orqali baholaydi (Transkript asosida).
    """
    if not OPENROUTER_API_KEY:
        return {"error": "API key not configured", "overall_score": 0}

    if not transcript_text or not transcript_text.strip():
        return {
            "overall_score": 0,
            "cefr_estimate": "A1",
            "criteria": [{"name": "Task Achievement", "score": 0, "max_score": 10, "comment": "No transcript provided."}],
            "strengths": [],
            "weaknesses": ["Audio was empty or could not be transcribed."],
            "recommendations": ["Please ensure your microphone is working and speak clearly."],
            "model_used": "validation"
        }

    word_count = len(transcript_text.strip().split())

    if not system_prompt:
        system_prompt = f"""You are a strict CEFR-certified English speaking examiner.
You are evaluating a SPEAKING transcript (not a written essay). 
Focus on how a spoken response would be evaluated based on this transcript.

CRITICAL RULES:
1. Evaluate based on CEFR {cefr_level} speaking criteria.
2. Be STRICT and REALISTIC. Do not give high scores for very short or irrelevant answers.
3. If the transcript is too short (under 30 words) or completely off-topic, give a very low score (0-20 range).
4. Respond ONLY with valid JSON.

TASK TOPIC: {task_instruction}
EXPECTED CEFR: {cefr_level}
RESPONSE DURATION: {duration_sec or 'Unknown'} seconds
WORD COUNT: {word_count} words

SCORING SCALE (0-100):
- 0-20: Very poor (too short, irrelevant, incomprehensible)
- 21-40: Poor (frequent pauses, basic vocabulary, many errors)
- 41-60: Fair (adequate communication, some errors, limited range)
- 61-80: Good (clear, good vocabulary, minor errors)
- 81-100: Excellent (fluent, wide vocabulary, accurate, natural)

You MUST respond with ONLY valid JSON:
{{
  "overall_score": <0-100 integer, BE STRICT>,
  "cefr_estimate": "<A1|A2|B1|B2|C1|C2>",
  "criteria": [
    {{
      "name": "Fluency & Coherence",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment on flow and linking>"
    }},
    {{
      "name": "Lexical Resource",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment on vocabulary>"
    }},
    {{
      "name": "Grammatical Range & Accuracy",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment on grammar>"
    }},
    {{
      "name": "Task Achievement",
      "score": <0-10>,
      "max_score": 10,
      "comment": "<brief comment on relevance to topic>"
    }}
  ],
  "corrections": [
    {{
      "original": "<wrong phrase from transcript>",
      "corrected": "<corrected phrase>",
      "explanation": "<why>"
    }}
  ],
  "strengths": ["<strength 1>"],
  "weaknesses": ["<weakness 1>"],
  "recommendations": ["<tip 1>"]
}}"""

    user_prompt = f"Student's spoken transcript ({word_count} words):\n\n{transcript_text}"

    last_error = None
    for model in _model_attempts():
        try:
            logger.info(f"🎤 Evaluating speaking with model: {model}")
            result = await _call_openrouter(model, system_prompt, user_prompt)

            if "overall_score" not in result:
                result["overall_score"] = 0
            
            ai_score_100 = result.get("overall_score", 0)
            normalized_score = (ai_score_100 / 100.0) * max_score
            
            result["overall_score_normalized"] = round(normalized_score, 2)
            result["overall_score_100"] = ai_score_100
            result["model_used"] = model
            
            logger.info(f"✅ Speaking evaluation success: {ai_score_100}/100 → {normalized_score:.2f}/{max_score}")
            return result

        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ Speaking model {model} failed: {e}")
            await asyncio.sleep(1.5)
            continue

    return {
        "error": f"All models failed. Last: {last_error}",
        "overall_score": 0,
        "overall_score_normalized": 0,
        "criteria": [],
        "model_used": None,
    }