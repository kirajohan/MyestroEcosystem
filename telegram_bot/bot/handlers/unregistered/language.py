"""Language selection for unregistered users."""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.keyboards.reply import get_level_selection_keyboard
from bot.states.registration import RegistrationState
from bot.utils.i18n import get_text

router = Router()


@router.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]))
async def language_selected(message: types.Message, state: FSMContext):
    """User selected language."""
    
    # Map button text to language code
    lang_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en"
    }
    
    lang = lang_map.get(message.text, "uz")
    
    # Save language to FSM
    await state.update_data(lang=lang)
    
    # Move to registration
    await state.set_state(RegistrationState.waiting_for_name)
    
    prompt_text = get_text("register.name_prompt", lang)
    await message.answer(prompt_text)