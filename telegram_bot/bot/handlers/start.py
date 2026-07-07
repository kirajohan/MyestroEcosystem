"""Start handler — /start command → language selection → main menu."""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.registration import StartSection
from bot.keyboards.reply import language_selection_keyboard, main_menu_keyboard
from bot.utils.i18n import get_text

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """Handle /start command — show welcome text + language selection keyboard."""
    await state.clear()
    await state.set_state(StartSection.language_selection)

    welcome_text = (
        "👋 *Assalomu alaykum! Myestro AI yordamchiga xush kelibsiz!*\n\n"
        "Myestro — bu ingliz tilini o'rganish uchun AI-powered bepul platforma.\n"
        "AI Teacher bilan suhbatlashing, imtihon topshiring va bilimingizni oshiring!\n\n"
        "🇺🇿 Iltimos, tilni tanlang:\n"
        "🇷🇺 Пожалуйста, выберите язык:\n"
        "🇬🇧 Please choose a language:"
    )

    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=language_selection_keyboard(),
    )


@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Handle /help command."""
    await message.answer(
        "🤖 *Myestro AI yordamchi boti*\n\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam\n\n"
        "Ingliz tilini o'rganishda AI Teacher yordam beradi!",
        parse_mode="Markdown",
    )

