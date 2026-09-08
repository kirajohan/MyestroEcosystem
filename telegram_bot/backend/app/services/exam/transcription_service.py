"""
Transcription Service — Audio ni matnga aylantirish (Speech-to-Text).
Groq API (Whisper) ishlatadi — bepul va tez.
"""

import logging
import os
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


async def transcribe_audio(
    audio_file_path: str,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Audio faylni Groq API (Whisper) orqali matnga aylantiradi.
    
    Args:
        audio_file_path: Audio faylning to'liq yo'li (masalan: /app/media/exam/audio/xxx.webm)
        language: Audio tili (default: "en" - ingliz)
    
    Returns:
        {
            "success": True,
            "transcript": "Hello, my name is...",
            "duration_sec": 45,
            "word_count": 120
        }
    """
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set in .env!")
        return {
            "success": False,
            "error": "GROQ_API_KEY not configured",
            "transcript": ""
        }

    try:
        logger.info(f"🎤 Transcribing audio: {audio_file_path}")
        
        # Faylni ochish
        with open(audio_file_path, "rb") as audio_file:
            # Groq API ga so'rov yuborish
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    GROQ_TRANSCRIBE_URL,
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                    },
                    files={
                        "file": (os.path.basename(audio_file_path), audio_file, "audio/webm"),
                    },
                    data={
                        "model": "whisper-large-v3",  # Eng yaxshi Whisper modeli
                        "language": language,
                        "response_format": "json",
                        "temperature": "0",
                    },
                )

        if response.status_code != 200:
            error_text = response.text[:300]
            logger.error(f"❌ Groq API error: {response.status_code} - {error_text}")
            return {
                "success": False,
                "error": f"Groq API error: {response.status_code}",
                "transcript": ""
            }

        data = response.json()
        transcript = data.get("text", "").strip()
        duration_sec = data.get("duration", 0)
        
        # So'zlar sonini hisoblash
        word_count = len(transcript.split()) if transcript else 0
        
        logger.info(f"✅ Transcription successful: {word_count} words, {duration_sec:.1f}s")
        
        return {
            "success": True,
            "transcript": transcript,
            "duration_sec": duration_sec,
            "word_count": word_count,
        }

    except FileNotFoundError:
        logger.error(f"❌ Audio file not found: {audio_file_path}")
        return {
            "success": False,
            "error": f"File not found: {audio_file_path}",
            "transcript": ""
        }
    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "transcript": ""
        }