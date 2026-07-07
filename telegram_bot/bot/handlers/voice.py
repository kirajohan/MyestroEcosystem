from aiogram import Router, types, F
import logging
from bot.utils.ai_client import (
    transcribe_voice_via_service,
    transcribe_voice,
    ask_ai,
    build_teacher_prompt,
)
from bot.config import settings

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def handle_voice(message: types.Message):
    """Handle voice messages — transcribe and respond."""
    try:
        file = await message.bot.get_file(message.voice.file_id)
        audio_bytes = await message.bot.download_file(file.file_path)
        audio_data = audio_bytes.read()

        # First try local whisper-service
        text = await transcribe_voice_via_service(audio_data)

        # Fallback to OpenRouter if local service failed
        if not text:
            logger.warning("whisper-service failed, falling back to OpenRouter")
            text = await transcribe_voice(audio_data)

        if not text:
            await message.answer("Could not transcribe audio. Please try again.")
            return

        # Send transcription
        await message.answer(f"📝 Transcription: {text}")

        # AI response
        system_prompt = build_teacher_prompt("A2", "uz")
        response = await ask_ai(
            prompt=f"Student said (transcribed from voice): {text}\nProvide feedback on pronunciation and grammar.",
            system_prompt=system_prompt,
        )
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        await message.answer("Error processing voice message.")

