# bot/handlers/register.py
"""Register handler — Registration flow with colored keyboards (Blue/Red/Green)."""

import re
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.registration import AuthFSM, RegisteredSection
from bot.keyboards.inline import main_menu_kb, confirm_kb
from bot.utils.i18n import get_text
from bot.utils.helpers import clean_telegram_text
from bot.config import settings
import httpx

router = Router()

# Backend API
REGISTER_INIT_URL = f"{settings.API_BASE_URL}/auth/register-init"


# ══════════════════════════════════════════════════════════════
# REGISTRATION FLOW
# ══════════════════════════════════════════════════════════════

@router.message(AuthFSM.waiting_name)
async def handle_name(message: types.Message, state: FSMContext):
    """Handle name input during registration — Blue keyboard."""
    name = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # ═══════════════════════════════════════════════════════════
    # SECURITY: Input sanitization
    # ═══════════════════════════════════════════════════════════
    name = clean_telegram_text(name)
    if len(name) < 2 or len(name) > 100:
        await message.answer(get_text("register.ask_name", lang))
        return

    await state.update_data(register_name=name)

    # If email was already provided, skip email step
    if user_data.get("register_email"):
        await state.set_state(AuthFSM.waiting_password_new)
        await message.answer(get_text("register.ask_password", lang))
    else:
        await state.set_state(AuthFSM.waiting_email)
        await message.answer(get_text("register.ask_email", lang))


@router.message(AuthFSM.waiting_email)
async def handle_email(message: types.Message, state: FSMContext):
    """Handle email input during registration — Blue keyboard."""
    email = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # ═══════════════════════════════════════════════════════════
    # SECURITY: Email validation
    # ═══════════════════════════════════════════════════════════
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer(
            get_text("register.invalid_email", lang),
        )
        return

    await state.update_data(register_email=email)
    await state.set_state(AuthFSM.waiting_password_new)

    await message.answer(
        get_text("register.ask_password", lang),
    )


@router.message(AuthFSM.waiting_password_new)
async def handle_password_new(message: types.Message, state: FSMContext):
    """Handle password creation during registration — Blue keyboard."""
    password = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # ═══════════════════════════════════════════════════════════
    # SECURITY: Strong password validation
    # ═══════════════════════════════════════════════════════════
    if len(password) < 8:
        await message.answer(
            get_text("register.invalid_password", lang),
        )
        return

    # Check for uppercase, lowercase, digit, special char
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    if not (has_upper and has_lower and has_digit and has_special):
        password_hints = {
            "uz": "🔐 Parol shunday bo'lishi kerak: bosh harf, kichik harf, raqam, maxsus belgi (@, #, $, etc.)",
            "ru": "🔐 Пароль должен содержать: заглавные, строчные буквы, цифры и спецсимволы (@, #, $, и т.д.)",
            "en": "🔐 Password must contain: uppercase, lowercase, digits, and special chars (@, #, $, etc.)"
        }
        await message.answer(
            password_hints.get(lang, password_hints["uz"]),
        )
        return

    await state.update_data(register_password=password)
    await state.set_state(AuthFSM.waiting_confirm_password)

    await message.answer(
        get_text("register.ask_confirm_password", lang),
    )


@router.message(AuthFSM.waiting_confirm_password)
async def handle_confirm_password(message: types.Message, state: FSMContext):
    """Handle password confirmation during registration."""
    confirm = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    password = user_data.get("register_password", "")

    if confirm != password:
        await message.answer(
            get_text("register.password_mismatch", lang),
        )
        return

    await state.set_state(AuthFSM.confirmation)

    name = user_data.get("register_name", "—")
    email = user_data.get("register_email", "—")
    phone = user_data.get("register_phone", "—")

    # Display confirmation — show with colored buttons
    confirmation_texts = {
        "uz": (
            f"✅ *Registratsiya ma'lumotlarini tasdiqlang:*\n\n"
            f"👤 *Ism:* {name}\n"
            f"📧 *Email:* {email}\n"
            f"📱 *Telefon:* {phone}\n\n"
            f"Hammasi to'g'rimi?"
        ),
        "ru": (
            f"✅ *Подтвердите данные регистрации:*\n\n"
            f"👤 *Имя:* {name}\n"
            f"📧 *Email:* {email}\n"
            f"📱 *Телефон:* {phone}\n\n"
            f"Всё верно?"
        ),
        "en": (
            f"✅ *Confirm registration details:*\n\n"
            f"👤 *Name:* {name}\n"
            f"📧 *Email:* {email}\n"
            f"📱 *Phone:* {phone}\n\n"
            f"Is everything correct?"
        )
    }

    await message.answer(
        confirmation_texts.get(lang, confirmation_texts["uz"]),
        parse_mode="Markdown",
        reply_markup=confirm_kb(lang),
    )


@router.callback_query(F.data == "confirm_yes")
async def confirm_registration_yes(callback: types.CallbackQuery, state: FSMContext):
    """Handle confirmation YES — submit registration."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    name = user_data.get("register_name", "")
    email = user_data.get("register_email", "")
    password = user_data.get("register_password", "")
    phone = user_data.get("register_phone", "")

    # Submit registration
    tokens, user_info = await _register_user(
        callback.from_user.id, name, email, password, phone,
    )
    
    if tokens and user_info:
        await _do_login_success(callback.message, state, user_info, lang)
    else:
        error_texts = {
            "uz": "❌ Registratsiya xatosi. Iltimos qayta urinib ko'ring.",
            "ru": "❌ Ошибка регистрации. Пожалуйста, попробуйте снова.",
            "en": "❌ Registration error. Please try again."
        }
        await callback.message.answer(
            error_texts.get(lang, error_texts["uz"]),
        )
        await state.set_state(RegisteredSection.main_menu)

    await callback.answer()


@router.callback_query(F.data == "confirm_no")
async def confirm_registration_no(callback: types.CallbackQuery, state: FSMContext):
    """Handle confirmation NO — restart registration."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # Clear registration data
    await state.update_data(
        register_name=None,
        register_email=None,
        register_password=None,
        register_confirm_password=None,
    )
    await state.set_state(AuthFSM.waiting_name)
    
    await callback.message.answer(
        get_text("register.ask_name", lang),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# BACKEND HELPERS
# ══════════════════════════════════════════════════════════════

async def _register_user(
    telegram_id: int, name: str, email: str, password: str, phone: str = "",
) -> tuple:
    """Register new user via backend API."""
    try:
        payload = {
            "telegram_id": telegram_id,
            "full_name": name,
            "email": email,
            "password": password,
            "phone": phone if phone else "",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                REGISTER_INIT_URL,
                json=payload,
            )
            if response.status_code in (200, 201):
                data = response.json()
                tokens = {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token"),
                }
                user_info = data.get("user", {})
                return tokens, user_info
            else:
                print(f"[REGISTER ERROR] Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
    return None, {}


async def _do_login_success(
    message: types.Message, state: FSMContext, user_info: dict, lang: str
):
    """Complete login and show registered menu."""
    
    update_data = {
        "registration_complete": True,
        "user_id": user_info.get("id"),
        "full_name": user_info.get("full_name", ""),
        "email": user_info.get("email", ""),
        "phone": user_info.get("phone", ""),
        "cefr_level": user_info.get("cefr_level", "A1"),
    }

    await state.set_state(RegisteredSection.main_menu)
    await state.update_data(**update_data)

    # Success message
    success_texts = {
        "uz": f"🎉 Xush kelibsiz, {user_info.get('full_name', '')}!",
        "ru": f"🎉 Добро пожаловать, {user_info.get('full_name', '')}!",
        "en": f"🎉 Welcome, {user_info.get('full_name', '')}!"
    }

    await message.answer(
        success_texts.get(lang, success_texts["uz"]),
    )

    # Welcome message with menu — BLUE/GREEN mixed colors
    welcome_texts = {
        "uz": (
            f"🎯 *Myestro platformasiga kirishdingiz!*\n\n"
            f"📚 Darsliklari oʻqing\n"
            f"🤖 AI Teacher bilan suhbatlashgan\n"
            f"📝 Imtihonlarni topshiring\n\n"
            f"Boshlash uchun tugmani tanlang:"
        ),
        "ru": (
            f"🎯 *Полный доступ к платформе Myestro!*\n\n"
            f"📚 Изучайте уроки\n"
            f"🤖 Общайтесь с AI Учителем\n"
            f"📝 Сдавайте экзамены\n\n"
            f"Выберите из меню ниже для начала:"
        ),
        "en": (
            f"🎯 *Full access to Myestro platform!*\n\n"
            f"📚 Study lessons\n"
            f"🤖 Chat with AI Teacher\n"
            f"📝 Take exams\n\n"
            f"Choose from menu below to get started:"
        )
    }

    await message.answer(
        welcome_texts.get(lang, welcome_texts["uz"]),
        parse_mode="Markdown",
        reply_markup=main_menu_kb(lang=lang)
    )

    # Optional: Show channel join message
    if settings.CHANNEL_ID and settings.CHANNEL_USERNAME:
        channel_texts = {
            "uz": (
                f"📢 <b>Yangiliklarga a'zo bo'lish</b>\n\n"
                f"Barcha darslik yangiliklarini, taklif va eksklyuziv ta'limlarga faqat kanalda chiqadi!\n\n"
                f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Kanalga a'zo bo'lish</a>"
            ),
            "ru": (
                f"📢 <b>Подписаться на обновления</b>\n\n"
                f"Все новые уроки, предложения и эксклюзивные материалы только в канале!\n\n"
                f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Подписаться на канал</a>"
            ),
            "en": (
                f"📢 <b>Subscribe to Updates</b>\n\n"
                f"All new lessons, offers, and exclusive materials only in the channel!\n\n"
                f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Subscribe to channel</a>"
            )
        }
        
        await message.answer(
            channel_texts.get(lang, channel_texts["uz"]),
            parse_mode="HTML",
        )