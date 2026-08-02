# bot/handlers/start.py

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from bot.states.registration import RegistrationFSM, RegisteredSection
from bot.keyboards.orange_keyboard import ColoredKeyboard
from bot.utils.i18n import get_text
from bot.config import settings
import httpx

router = Router()

CHECK_USER_URL = f"{settings.API_BASE_URL}/sync/user/"


# ══════════════════════════════════════════════════════════════
# /start COMMAND
# ══════════════════════════════════════════════════════════════

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """Handle /start command — check DB and route accordingly."""
    telegram_id = message.from_user.id

    # Check if user already registered in DB
    user_data = None
    user_lang = "uz"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CHECK_USER_URL}{telegram_id}")
            if response.status_code == 200:
                user_data = response.json()
                user_lang = user_data.get("lang", "uz")
    except Exception as e:
        print(f"[START CHECK USER ERROR] {e}")

    if user_data:
        # ── REGISTERED USER ──
        # Load profile and language from DB
        await state.clear()
        await state.set_state(RegisteredSection.main_menu)
        
        # Store user data in state for quick access
        await state.update_data(
            telegram_id=telegram_id,
            lang=user_lang,
            registration_complete=True,
            id=user_data.get("id"),
            phone=user_data.get("phone"),
            name=user_data.get("name"),
        )

        # Get welcome text based on language
        welcome_text = get_text(
            "registered.welcome_back",
            user_lang,
            name=user_data.get("name", "User"),
            last_active=user_data.get("last_active", "bugun"),
            streak=user_data.get("streak", 0),
        )

        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=ColoredKeyboard.reply_main_menu(lang=user_lang),
        )
    else:
        # ── NEW USER ──
        # Show language selection
        await state.clear()
        await state.set_state(RegistrationFSM.phone_request)

        welcome_text = (
            "👋 <b>Assalomu alaykum! Myestro AI yordamchiga xush kelibsiz!</b>\n\n"
            "Myestro — bu ingliz tilini o'rganish uchun AI-powered bepul platforma.\n"
            "AI Teacher bilan suhbatlashing, imtihon topshiring va bilimingizni oshiring!\n\n"
            "🇺🇿 Iltimos, tilni tanlang:\n"
            "🇷🇺 Пожалуйста, выберите язык:\n"
            "🇬🇧 Please choose a language:"
        )

        await message.answer(
            welcome_text,
            parse_mode="HTML",
            reply_markup=ColoredKeyboard.reply_start_menu(lang="uz"),
        )


# ══════════════════════════════════════════════════════════════
# LANGUAGE SELECTION (for new users from /start)
# ══════════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]),
    StateFilter(RegistrationFSM.phone_request),
)
async def language_selected_for_registration(message: types.Message, state: FSMContext):
    """Handle language selection from /start for new users."""
    lang_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
    }
    lang = lang_map.get(message.text, "uz")
    
    # Save language to FSM data
    await state.update_data(lang=lang)
    
    # Keep state as phone_request
    await state.set_state(RegistrationFSM.phone_request)

    # Get phone request text
    phone_request_text = get_text("registration.phone_request", lang)

    await message.answer(
        phone_request_text,
        parse_mode="HTML",
        reply_markup=ColoredKeyboard.reply_contact(lang=lang),
    )


# ══════════════════════════════════════════════════════════════
# PHONE CONTACT HANDLER (for new users)
# ══════════════════════════════════════════════════════════════

@router.message(
    F.contact,
    StateFilter(RegistrationFSM.phone_request),
)
async def handle_phone_contact_new_user(message: types.Message, state: FSMContext):
    """Handle phone contact from new user — save to DB and show main menu."""
    # Verify the contact belongs to the user
    if message.contact.user_id != message.from_user.id:
        user_data = await state.get_data()
        lang = user_data.get("lang", "uz")
        await message.answer(get_text("contact.not_own", lang))
        return

    phone_number = message.contact.phone_number
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    telegram_id = message.from_user.id

    # Save user to DB
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "telegram_id": telegram_id,
                "phone": phone_number,
                "lang": lang,
            }
            response = await client.post(f"{settings.API_BASE_URL}/sync/user/", json=payload)
            
            if response.status_code in (200, 201):
                user_data_db = response.json()
                user_id = user_data_db.get("id")
                
                # Update state with user data
                await state.update_data(
                    telegram_id=telegram_id,
                    phone=phone_number,
                    lang=lang,
                    registration_complete=True,
                    id=user_id,
                )
            else:
                print(f"[PHONE SAVE ERROR] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[PHONE SAVE ERROR] {e}")

    # Set state to registered main menu
    await state.set_state(RegisteredSection.main_menu)

    # Get welcome text
    welcome_text = get_text("registered.welcome_new", lang)

    await message.answer(
        welcome_text,
        parse_mode="HTML",
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
    )


# ══════════════════════════════════════════════════════════════
# /help COMMAND
# ══════════════════════════════════════════════════════════════

@router.message(Command("help"))
async def help_handler(message: types.Message, state: FSMContext):
    """Show help message with all available commands."""
    # Get user language from state
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    
    # Get user's name if available
    name = user_data.get("name", "User")
    
    # Build help text based on language
    help_texts = {
        "uz": (
            f"👋 <b>Assalomu alaykum, {name}!</b>\n\n"
            "📋 <b>Bot buyruqlari ro'yxati:</b>\n\n"
            "🚀 <b>/start</b> — Botni ishga tushirish\n"
            "❓ <b>/help</b> — Yordam va buyruqlar ro'yxati\n"
            "📱 <b>/menu</b> — Asosiy menyuni ko'rish\n"
            "🌐 <b>/language</b> — Tilni o'zgartirish\n"
            "⚙️ <b>/settings</b> — Sozlamalar\n"
            "👤 <b>/profile</b> — Profil ma'lumotlari\n"
            "📨 <b>/admin</b> — Admin bilan aloqa\n\n"
            "💡 <b>Maslahat:</b> Botdan to'liq foydalanish uchun ro'yxatdan o'ting!"
        ),
        "ru": (
            f"👋 <b>Здравствуйте, {name}!</b>\n\n"
            "📋 <b>Список команд бота:</b>\n\n"
            "🚀 <b>/start</b> — Запустить бота\n"
            "❓ <b>/help</b> — Помощь и список команд\n"
            "📱 <b>/menu</b> — Показать главное меню\n"
            "🌐 <b>/language</b> — Изменить язык\n"
            "⚙️ <b>/settings</b> — Настройки\n"
            "👤 <b>/profile</b> — Профиль\n"
            "📨 <b>/admin</b> — Связаться с админом\n\n"
            "💡 <b>Совет:</b> Зарегистрируйтесь для полного доступа!"
        ),
        "en": (
            f"👋 <b>Hello, {name}!</b>\n\n"
            "📋 <b>Bot Commands List:</b>\n\n"
            "🚀 <b>/start</b> — Start the bot\n"
            "❓ <b>/help</b> — Help and commands list\n"
            "📱 <b>/menu</b> — Show main menu\n"
            "🌐 <b>/language</b> — Change language\n"
            "⚙️ <b>/settings</b> — Settings\n"
            "👤 <b>/profile</b> — Profile information\n"
            "📨 <b>/admin</b> — Contact admin\n\n"
            "💡 <b>Tip:</b> Register to get full access!"
        ),
    }

    help_text = help_texts.get(lang, help_texts["uz"])

    await message.answer(
        help_text,
        parse_mode="HTML",
    )


# ══════════════════════════════════════════════════════════════
# LEGACY /menu COMMAND (kept for backward compatibility)
# ══════════════════════════════════════════════════════════════

@router.message(Command("menu"))
async def menu_handler(message: types.Message, state: FSMContext):
    """Show main menu with colored buttons."""
    user_data = await state.get_data()
    user_lang = user_data.get("lang", "uz")
    
    await message.answer(
        get_text("main_menu", user_lang),
        parse_mode="HTML",
        reply_markup=ColoredKeyboard.reply_main_menu(lang=user_lang),
    )