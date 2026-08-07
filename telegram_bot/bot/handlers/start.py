# bot/handlers/start.py

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from bot.states.registration import RegistrationFSM, RegisteredSection
from bot.keyboards.inline import (
    cefr_level_selection, main_menu_kb, phone_share_kb, start_menu_kb,
)
from bot.utils.i18n import get_text
from bot.config import settings
import httpx
import re

router = Router()

CHECK_USER_URL = f"{settings.API_BASE_URL}/sync/user"


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
            reply_markup=main_menu_kb(lang=user_lang),
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
            reply_markup=start_menu_kb(lang="uz"),
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
        reply_markup=phone_share_kb(lang=lang),
    )


# ══════════════════════════════════════════════════════════════
# PHONE CONTACT HANDLER (for new users)
# ══════════════════════════════════════════════════════════════

@router.message(
    F.contact,
    StateFilter(RegistrationFSM.phone_request),
)
async def handle_phone_contact_new_user(message: types.Message, state: FSMContext):
    """Handle phone contact from new user — ask for NAME (mandatory registration)."""
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

    # ✅ Save phone to state (don't create user yet)
    await state.update_data(
        telegram_id=telegram_id,
        phone=phone_number,
        lang=lang,
    )

    # → Move to NAME input
    await state.set_state(RegistrationFSM.waiting_name)

    # Ask for full name
    ask_name_texts = {
        "uz": "👤 <b>Iltimos, to'liq ism-familiyangizni kiriting:</b>\n\n<i>Masalan: Ali Rakhmonov</i>",
        "ru": "👤 <b>Пожалуйста, введите ваше полное имя:</b>\n\n<i>Например: Иван Иванов</i>",
        "en": "👤 <b>Please enter your full name:</b>\n\n<i>For example: John Smith</i>",
    }
    
    await message.answer(
        ask_name_texts.get(lang, ask_name_texts["uz"]),
        parse_mode="HTML",
    )


# ══════════════════════════════════════════════════════════════
# NAME INPUT HANDLER — NEW
# ══════════════════════════════════════════════════════════════

@router.message(StateFilter(RegistrationFSM.waiting_name))
async def handle_name_input(message: types.Message, state: FSMContext):
    """Handle name input from user — validate and ask for EMAIL."""
    full_name = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # Validate name (at least 2 characters, max 100)
    if len(full_name) < 2 or len(full_name) > 100:
        validation_texts = {
            "uz": "❌ Ism 2-100 ta belgi uzunligida bo'lishi kerak!",
            "ru": "❌ Имя должно быть от 2 до 100 символов!",
            "en": "❌ Name must be between 2 and 100 characters!",
        }
        await message.answer(validation_texts.get(lang, validation_texts["uz"]))
        return

    # ✅ Save name to state
    await state.update_data(full_name=full_name)

    # → Move to EMAIL input
    await state.set_state(RegistrationFSM.waiting_email)

    # Ask for email
    ask_email_texts = {
        "uz": "📧 <b>Email manzilingizni kiriting:</b>\n\n<i>Masalan: user@example.com</i>",
        "ru": "📧 <b>Введите ваш адрес электронной почты:</b>\n\n<i>Например: user@example.com</i>",
        "en": "📧 <b>Please enter your email address:</b>\n\n<i>For example: user@example.com</i>",
    }
    
    await message.answer(
        ask_email_texts.get(lang, ask_email_texts["uz"]),
        parse_mode="HTML",
    )


# ══════════════════════════════════════════════════════════════
# EMAIL INPUT HANDLER — NEW
# ══════════════════════════════════════════════════════════════

@router.message(StateFilter(RegistrationFSM.waiting_email))
async def handle_email_input(message: types.Message, state: FSMContext):
    """Handle email input from user — validate and ask for CEFR level."""
    email = message.text.strip().lower()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # Simple email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        validation_texts = {
            "uz": "❌ Email formati notog'ri! Iltimos, to'g'ri email kiriting.",
            "ru": "❌ Неверный формат электронной почты! Пожалуйста, введите существующий адрес электронной почты.",
            "en": "❌ Invalid email format! Please enter a valid email address.",
        }
        await message.answer(validation_texts.get(lang, validation_texts["uz"]))
        return

    # ✅ Save email to state
    await state.update_data(email=email)

    # → Move to LEVEL selection
    await state.set_state(RegistrationFSM.waiting_level)

    # Ask for CEFR level
    ask_level_texts = {
        "uz": "📊 <b>Inglis tilida qaysi darajasiz turibsiz?</b>\n\nA0 - Hech qanday bilim yok\nA1 - Boshlang'ich\nA2 - Elementar\nB1 - O'rta\nB2 - Yuqori o'rta\nC1 - Advanced\nC2 - Mutaxassis",
        "ru": "📊 <b>Какой уровень английского языка у вас?</b>\n\nA0 - Нет знаний\nA1 - Начинающий\nA2 - Элементарный\nB1 - Средненний\nB2 - Выше среднего\nC1 - Продвинутый\nC2 - Владение в совершенстве",
        "en": "📊 <b>What is your current English level?</b>\n\nA0 - No knowledge\nA1 - Beginner\nA2 - Elementary\nB1 - Intermediate\nB2 - Upper-Intermediate\nC1 - Advanced\nC2 - Proficiency",
    }
    
    await message.answer(
        ask_level_texts.get(lang, ask_level_texts["uz"]),
        parse_mode="HTML",
        reply_markup=cefr_level_selection(),
    )


# ══════════════════════════════════════════════════════════════
# LEVEL SELECTION CALLBACK — NEW
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("level_"), StateFilter(RegistrationFSM.waiting_level))
async def handle_level_selection(callback: types.CallbackQuery, state: FSMContext):
    """Handle CEFR level selection — create user in DB and show main menu."""
    level = callback.data.split("_")[1]  # Extract level from callback data
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    telegram_id = user_data.get("telegram_id")
    phone = user_data.get("phone")
    full_name = user_data.get("full_name")

    # ✅ Save level to state
    await state.update_data(cefr_level=level)

    # → Create user in DB with all registration data
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "telegram_id": telegram_id,
                "phone": phone,
                "email": user_data.get("email", ""),
                "full_name": full_name,
                "cefr_level": level,
                "lang": lang,
                "auth_provider": "telegram",
            }
            response = await client.post(
                f"{settings.API_BASE_URL}/sync/user",
                json=payload
            )
            
            if response.status_code in (200, 201):
                user_data_db = response.json()
                user_id = user_data_db.get("id")
                
                # Update state with full user data
                await state.update_data(
                    id=user_id,
                    registration_complete=True,
                )
            else:
                error_texts = {
                    "uz": f"❌ Ro'yxatdan o'tishda xato: {response.status_code}",
                    "ru": f"❌ Ошибка при регистрации: {response.status_code}",
                    "en": f"❌ Registration error: {response.status_code}",
                }
                await callback.message.edit_text(
                    error_texts.get(lang, error_texts["uz"])
                )
                await callback.answer()
                return
    except Exception as e:
        print(f"[REGISTRATION ERROR] {e}")
        error_texts = {
            "uz": "❌ Ro'yxatdan o'tishda xato yuz berdi!",
            "ru": "❌ Произошла ошибка при регистрации!",
            "en": "❌ An error occurred during registration!",
        }
        await callback.message.edit_text(
            error_texts.get(lang, error_texts["uz"])
        )
        await callback.answer()
        return

    # → Set state to REGISTERED MAIN MENU
    await state.set_state(RegisteredSection.main_menu)

    # Welcome message
    welcome_texts = {
        "uz": f"✅ <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>\n\n👋 Xush kelibsiz, <b>{full_name}</b>!\n\n📊 Daraj: <b>{level}</b>\n📧 Email: <b>{user_data.get('email', 'N/A')}</b>\n📞 Telefon: <b>{phone}</b>\n\n🎉 Endi asosiy menyuni foydalana olasiz!",
        "ru": f"✅ <b>Регистрация успешна!</b>\n\n👋 Добро пожаловать, <b>{full_name}</b>!\n\n📊 Уровень: <b>{level}</b>\n📧 Email: <b>{user_data.get('email', 'N/A')}</b>\n📞 Номер: <b>{phone}</b>\n\n🎉 Теперь вы можете использовать главное меню!",
        "en": f"✅ <b>Registration successful!</b>\n\n👋 Welcome, <b>{full_name}</b>!\n\n📊 Level: <b>{level}</b>\n📧 Email: <b>{user_data.get('email', 'N/A')}</b>\n📞 Phone: <b>{phone}</b>\n\n🎉 You can now use the main menu!",
    }

    await callback.message.edit_text(
        welcome_texts.get(lang, welcome_texts["uz"]),
        parse_mode="HTML",
        reply_markup=None,
    )

    # Send main menu
    await callback.message.answer(
        "📋 <b>Asosiy menyu</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(lang=lang),
    )

    await callback.answer()


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
        reply_markup=main_menu_kb(lang=user_lang),
    )
