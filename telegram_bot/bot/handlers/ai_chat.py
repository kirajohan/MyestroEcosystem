"""AI chat handler with memory system integration."""

import logging
from aiogram.filters import Command, StateFilter
from aiogram import types, F, Router
from bot.utils.ai_client import stream_ask_ai
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
import asyncio

from bot.config import settings
from bot.utils.ai_memory_client import AIMemoryClient


logger = logging.getLogger(__name__)
router = Router()

MAX_TEXT_LENGTH = 4000

# FSM States
class AIChat(StatesGroup):
    waiting_for_message = State()
    processing = State()


@router.message(Command("ai"))
async def cmd_start_ai(message: types.Message, state: FSMContext):
    """Start AI conversation with /ai command."""
    lang = "uz"  # Default language, can be from user profile
    
    # FIX: Set state so messages are routed to handler
    await state.set_state(AIChat.waiting_for_message)
    
    await message.answer(
        f"{get_text('ai.welcome', lang)}\n\n"
        "💬 Menga savollaringizni yo'llang, men sizga javob beraman.",
        parse_mode="HTML"
    )


@router.message(StateFilter(AIChat.waiting_for_message), F.text)
async def handle_ai_message_with_memory(message: Message, state: FSMContext):
    """Handle user message in AI chat with memory."""
    
    if message.text.startswith("/"):
        if message.text == "/stop":
            await state.clear()
            await message.answer("AI Chat ended.")
            return
        return
    
    user_id = message.from_user.id
    user_message = message.text
    
    # Show typing indicator
    await message.chat.send_action("typing")
    
    try:
        # Get AI memory client
        ai_memory_client = AIMemoryClient(
            backend_url=settings.BACKEND_URL,
            http_client=None
        )
        
        # Query AI with memory
        logger.info(f"User {user_id} AI query: {user_message[:50]}...")
        
        response_data = await ai_memory_client.query_with_memory(
            user_id=user_id,
            message=user_message,
            system_prompt=None,
            model=None
        )
        
        logger.debug(f"Response data type: {type(response_data)}")
        
        # Handle both dict and object responses
        if isinstance(response_data, dict):
            response_text = response_data.get("response", "Sorry, I couldn't generate a response.")
            model_used = response_data.get("model_used", "unknown")
            tokens = response_data.get("tokens_used")
            time_ms = response_data.get("processing_time_ms", 0)
        else:
            # Object response (Pydantic model)
            response_text = response_data.response
            model_used = response_data.model_used
            tokens = response_data.tokens_used
            time_ms = response_data.processing_time_ms
        
        # Add footer with metadata
        footer = f"\n\n_Model: {model_used} | Time: {time_ms}ms_"
        
        # Send response (chunk if too long)
        full_response = response_text + footer
        if len(full_response) > 4096:
            # Split into chunks of 4000 chars
            chunks = [full_response[i:i+4000] for i in range(0, len(full_response), 4000)]
            for chunk in chunks:
                await message.answer(chunk, parse_mode="Markdown")
                await asyncio.sleep(0.5)  # Rate limiting
        else:
            await message.answer(full_response, parse_mode="Markdown")
        
        logger.info(f"Response sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}", exc_info=True)
        error_msg = f"{get_text('ai_chat.error', message.from_user.language_code or 'uz')}"
        await message.answer(error_msg or f"❌ Error: {str(e)}")


@router.message(Command("ai_clear"))
async def clear_ai_memory(message: Message):
    """Clear AI memory for this user."""
    user_id = message.from_user.id
    
    try:
        ai_memory_client = AIMemoryClient(
            backend_url=settings.BACKEND_URL,
            http_client=None
        )
        result = await ai_memory_client.clear_memory(user_id)
        
        # Handle both dict and object
        if isinstance(result, dict):
            status = result.get("status")
        else:
            status = getattr(result, "status", None)
        
        if status == "success":
            text = "✓ AI memory cleared! Starting fresh conversation."
        else:
            text = "Failed to clear memory. Try again later."
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        await message.answer("❌ Error clearing memory")


@router.message(StateFilter(AIChat.waiting_for_message), F.voice)
async def handle_voice_message(message: Message, state: FSMContext):
    """Handle voice messages in AI chat (transcribe + query)."""
    
    user_id = message.from_user.id
    
    # Show processing indicator
    processing_msg = await message.answer("🎤 Processing voice message...")
    
    try:
        # Download voice file
        file_info = await message.bot.get_file(message.voice.file_id)
        voice_bytes = await message.bot.download_file(file_info.file_path)
        
        # TODO: Integrate speech-to-text (Telegram API or Whisper)
        # For now, just acknowledge
        await processing_msg.delete()
        await message.answer("Voice message received! (Transcription coming soon)")
        
    except Exception as e:
        logger.error(f"Error handling voice: {e}")
        await processing_msg.delete()
        await message.answer("❌ Error processing voice message")
