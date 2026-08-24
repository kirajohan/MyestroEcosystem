# bot/utils/api_client.py
"""
Backend API bilan bog'lanish uchun utility funksiyalar.
"""

import os
import httpx
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Backend API bazaviy URL
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:8002")


# ══════════════════════════════════════════════════════════════
# TESTS (QUIZ) API
# ══════════════════════════════════════════════════════════════

async def fetch_public_tests(
    cefr_level: str,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Faol testlar ro'yxatini olish (CEFR daraja bo'yicha).
    
    Returns:
        Testlar ro'yxati: [{"id": 1, "title": "...", "cefr_level": "A1", ...}, ...]
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{API_BASE_URL}/api/tests",
                params={
                    "level": cefr_level,
                    "limit": limit,
                    "offset": offset,
                    "active_only": True
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("tests", []) if isinstance(data, dict) else data
    except Exception as e:
        logger.error(f"Testlarni olishda xatolik: {e}")
        return []


async def fetch_test_questions(test_id: int) -> Optional[Dict[str, Any]]:
    """
    Test savollarini olish (Telegram Quiz Poll formatida).
    
    Returns:
        {
            "id": 1,
            "title": "A1 Grammar Test",
            "passing_score": 60,
            "questions": [
                {
                    "id": 101,
                    "question_text": "Choose the correct verb...",
                    "options": ["go", "goes", "going", "gone"],
                    "correct_option_index": 1,
                    "explanation": "'She' 3-shaxs birlik..."
                }
            ]
        }
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{API_BASE_URL}/api/tests/{test_id}/questions"
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Test savollarini olishda xatolik (test_id={test_id}): {e}")
        return None
# bot/utils/api_client.py

async def submit_test_attempt(
    user_id: int,
    test_id: int,
    score: int,
    total_questions: int,
    percentage: int,
    passed: bool
) -> bool:
    """Test natijasini backendga yuborish."""
    try:
        payload = {
            "user_id": user_id,
            "test_id": test_id,
            "score": score,
            "total_questions": total_questions,
            "percentage": percentage,
            "passed": passed
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/tests/attempts",  # ← BU YER: /api/test_attempts emas, /api/tests/attempts
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Test natijasi saqlandi: user={user_id}, test={test_id}, score={score}/{total_questions}")
            return True
    except Exception as e:
        logger.error(f"Test natijasini yuborishda xatolik: {e}")
        return False