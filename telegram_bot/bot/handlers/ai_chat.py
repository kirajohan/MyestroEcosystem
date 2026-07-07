"""AI Chat handler — /ai command to start AI conversation.

Phase 7: Activate AI chat mode
- /ai command starts interactive AI conversation
- Simple text-based conversation without FSM
- Supports streaming responses
- Graceful AI guard middleware integration
"""

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from bot.utils.ai_client import stream_ask_ai
from bot.utils.ai_prompts import build_system_prompt
from bot.utils.i18n import get_text

logger = logging.getLogger(__name__)
router = Router()

MAX_TEXT_LENGTH = 4000


@router.message(Command("ai"))
async def cmd_start_ai(message: types.Message):
    """Start AI conversation with /ai command."""
    lang = "uz"  # Default language, can be from user profile
    
    await message.answer(
        f"{get_text('ai.welcome', lang)}\n\n"
        "💬 Menga savollaringizni yo'llang, men sizga javob beraman.",
        parse_mode="HTML"
    )


@router.message(F.text, Command("ai"))
async def ai_handler(message: types.Message):
    """Handle AI chat messages (if text follows /ai command)."""
    lang = "uz"
    text = message.text.replace("/ai", "").strip()
    
    if not text:
        await message.answer("Iltimos, savol yoki matnni yozing.")
        return
    
    await handle_ai_message(message, text, lang)


async def handle_ai_message(message: types.Message, user_text: str, lang: str):
    """Process AI message with streaming."""
    if not user_text or len(user_text) > MAX_TEXT_LENGTH:
        await message.answer(get_text("ai.error", lang))
        return
    
    # Show thinking indicator
    thinking_msg = await message.answer("🤔 Fikr qilyapman...")
    
    try:
        # Build system prompt
        cefr_level = "B1"  # Default, can be from user profile
        system_prompt = build_system_prompt(lang, cefr_level)
        
        # Stream AI response
        full_response = ""
        async for chunk in stream_ask_ai(
            prompt=user_text,
            system_prompt=system_prompt,
        ):
            full_response += chunk
        
        # Send response
        if len(full_response) > MAX_TEXT_LENGTH:
            full_response = full_response[:MAX_TEXT_LENGTH - 3] + "..."
        
        await thinking_msg.edit_text(full_response, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"AI error: {e}", exc_info=True)
        await thinking_msg.edit_text(
            "❌ " + get_text("ai.error", lang)
        )
