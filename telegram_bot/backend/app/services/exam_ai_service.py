"""
AI Evaluation Service for Writing & Speaking.
OpenRouter API orqali ishlaydi.
"""

import json
import logging
import os
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash-preview"


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
    Qaytaradi: structured JSON natija.
    """
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY not set!")
        return {"error": "API key not configured", "overall_score": 0}

    # Default system prompt (agar rubricadan kelmagan bo'lsa)
    if not system_prompt:
        system_prompt = f"""You are an expert English language examiner specializing in CEFR assessment.

Evaluate the student's writing based on CEFR {cefr_level} criteria.

TASK: {task_instruction}
{"MIN WORDS: " + str(min_words) if min_words else ""}
{"MAX WORDS: " + str(max_words) if max_words else ""}

STUDENT ANSWER:
{student_text}

You MUST respond with ONLY valid JSON (no markdown, no explanation):
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

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://myestro.uz",
                    "X-Title": "Myestro Exam AI",
                },
                json={
                    "model": DEFAULT_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Evaluate this writing:\n\n{student_text}"},
                    ],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )

            if response.status_code != 200:
                logger.error(f"OpenRouter error: {response.status_code} - {response.text}")
                return {"error": f"AI service error: {response.status_code}", "overall_score": 0}

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # JSON parse qilish
            result = json.loads(content)

            # Validatsiya
            if "overall_score" not in result:
                result["overall_score"] = 0
            if "criteria" not in result:
                result["criteria"] = []

            logger.info(f"✅ Writing evaluated: score={result.get('overall_score')}")
            return result

    except json.JSONDecodeError as e:
        logger.error(f"AI returned invalid JSON: {e}")
        return {"error": "Invalid AI response format", "overall_score": 0, "raw_response": content}
    except Exception as e:
        logger.error(f"AI evaluation failed: {e}")
        return {"error": str(e), "overall_score": 0}