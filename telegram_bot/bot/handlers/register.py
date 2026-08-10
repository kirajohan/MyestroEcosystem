"""Auth handler — Unified Register/Login flow.

Flow:
1. 📝 Register/Login → Telefon raqam so'raydi (contact share yoki text)
2. Contact share → DB tekshir → found: avto-login | not found: registratsiya
3. Text (phone/email) → DB tekshir → found: parol so'ra | not found: registratsiya
4. Registratsiya: Ism → Email → Parol → Confirm → avto-login
"""

import re
from typing import Optional
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.registration import AuthFSM, RegisteredSection, StartSection
from bot.keyboards.reply import (
    remove_keyboard, confirm_kb , contact_request_keyboard,
    registered_menu_kb,
)
from bot.utils.i18n import get_text
from bot.config import settings
import httpx

router = Router()

# Backend API
CHECK_PHONE_URL = f"{settings.API_BASE_URL}/auth/check-phone"
CHECK_EMAIL_URL = f"{settings.API_BASE_URL}/auth/check-email"
PHONE_LOGIN_URL = f"{settings.API_BASE_URL}/auth/phone-login"
EMAIL_LOGIN_URL = f"{settings.API_BASE_URL}/auth/login"
REGISTER_INIT_URL = f"{settings.API_BASE_URL}/auth/register-init"


# ══════════════════════════════════════════════════════════════
# START AUTH FLOW
# ══════════════════════════════════════════════════════════════

@router.message(F.text.in_([
    "📝 Register/Login", "📝 Регистрация/Вход", "📝 Register/Login",
]))
async def start_auth(message: types.Message, state: FSMContext):
    """Start unified auth flow — ask for phone number."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    await state.set_state(AuthFSM.requesting_contact)
    await state.update_data(_flow=None)

    await message.answer(
        get_text("auth.phone_request", lang),
        reply_markup=contact_request_keyboard(),
    )


# ══════════════════════════════════════════════════════════════
# TEXT INPUT (Phone or Email)
# ══════════════════════════════════════════════════════════════

# NOTE: Contact share handler is in contact.py (AuthFSM.requesting_contact)

@router.message(AuthFSM.requesting_contact)
async def handle_phone_or_email(message: types.Message, state: FSMContext):
    """Handle text input: phone number or email."""
    text = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # Determine if it's phone or email
    phone = _parse_phone(text)
    email = _parse_email(text)

    if phone:
        # It's a phone number
        exists, user_info = await _check_phone(phone)
        if exists:
            # Ask for password
            await state.update_data(
                _flow="login",
                login_credential=phone,
                credential_type="phone",
            )
            await state.set_state(AuthFSM.waiting_password)
            await message.answer(
                get_text("login.ask_password", lang),
                reply_markup=remove_keyboard,
            )
        else:
            # Not found → register with phone
            await state.update_data(register_phone=phone, _flow="register")
            await state.set_state(AuthFSM.waiting_name)
            await message.answer(
                get_text("auth.phone_not_found", lang),
                reply_markup=remove_keyboard,
            )
            await message.answer(
                get_text("register.ask_name", lang),
                reply_markup=remove_keyboard,
            )
    elif email:
        # It's an email
        exists, user_info = await _check_email(email)
        if exists:
            # Ask for password
            await state.update_data(
                _flow="login",
                login_credential=email,
                credential_type="email",
            )
            await state.set_state(AuthFSM.waiting_password)
            await message.answer(
                get_text("login.ask_password", lang),
                reply_markup=remove_keyboard,
            )
        else:
            # Not found → register with email
            await state.update_data(register_email=email, _flow="register")
            await state.set_state(AuthFSM.waiting_name)
            await message.answer(
                get_text("auth.email_not_found", lang),
                reply_markup=remove_keyboard,
            )
            await message.answer(
                get_text("register.ask_name", lang),
                reply_markup=remove_keyboard,
            )
    else:
        # Invalid input
        await message.answer(
            get_text("auth.invalid_phone_or_email", lang),
            reply_markup=contact_request_keyboard(),
        )


# ══════════════════════════════════════════════════════════════
# LOGIN PASSWORD
# ══════════════════════════════════════════════════════════════

@router.message(AuthFSM.waiting_password)
async def handle_login_password(message: types.Message, state: FSMContext):
    """Handle password for login."""
    password = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    credential = user_data.get("login_credential", "")
    credential_type = user_data.get("credential_type", "")

    if credential_type == "phone":
        success, user_info, tokens = await _login_by_phone(
            message.from_user.id, credential, password
        )
    elif credential_type == "email":
        success, user_info, tokens = await _login_by_email(credential, password)
    else:
        success = False
        user_info = {}
        tokens = None

    if success:
        await _do_login(message, state, user_info, credential, tokens)
    else:
        await message.answer(
            get_text("login.wrong_password", lang),
            reply_markup=remove_keyboard,
        )
        await state.set_state(StartSection.main_menu)


# ══════════════════════════════════════════════════════════════
# REGISTRATION FLOW
# ══════════════════════════════════════════════════════════════

@router.message(AuthFSM.waiting_name)
async def handle_name(message: types.Message, state: FSMContext):
    """Handle name input."""
    name = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    if len(name) < 2 or len(name) > 100:
        await message.answer(get_text("register.ask_name", lang))
        return

    await state.update_data(register_name=name)

    # If email was already provided (e.g., user typed email to start), skip email step
    if user_data.get("register_email"):
        await state.set_state(AuthFSM.waiting_password_new)
        await message.answer(
            get_text("register.ask_password", lang),
            reply_markup=remove_keyboard,
        )
    else:
        await state.set_state(AuthFSM.waiting_email)
        await message.answer(
            get_text("register.ask_email", lang),
            reply_markup=remove_keyboard,
        )


@router.message(AuthFSM.waiting_email)
async def handle_email(message: types.Message, state: FSMContext):
    """Handle email input."""
    email = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer(get_text("register.invalid_email", lang))
        return

    await state.update_data(register_email=email)
    await state.set_state(AuthFSM.waiting_password_new)

    await message.answer(
        get_text("register.ask_password", lang),
        reply_markup=remove_keyboard,
    )


@router.message(AuthFSM.waiting_password_new)
async def handle_password_new(message: types.Message, state: FSMContext):
    """Handle password creation."""
    password = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    if len(password) < 8:
        await message.answer(get_text("register.invalid_password", lang))
        return

    await state.update_data(register_password=password)
    await state.set_state(AuthFSM.waiting_confirm_password)

    await message.answer(
        get_text("register.ask_confirm_password", lang),
        reply_markup=remove_keyboard,
    )


@router.message(AuthFSM.waiting_confirm_password)
async def handle_confirm_password(message: types.Message, state: FSMContext):
    """Handle password confirmation."""
    confirm = message.text.strip()
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    password = user_data.get("register_password", "")

    if confirm != password:
        await message.answer(get_text("register.password_mismatch", lang))
        return

    await state.set_state(AuthFSM.confirmation)

    name = user_data.get("register_name", "—")
    email = user_data.get("register_email", "—")
    phone = user_data.get("register_phone", "—")

    await message.answer(
        get_text("register.confirm", lang, name=name, email=email, phone=phone),
        reply_markup=confirm_kb (lang),
    )


@router.message(AuthFSM.confirmation)
async def handle_confirmation(message: types.Message, state: FSMContext):
    """Handle confirmation — submit or restart."""
    text = message.text.strip()
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    confirm_texts = ["✅ Ha", "✅ Да", "✅ Yes"]  # uz, ru, en
    restart_texts = ["❌ Yo'q", "❌ Нет", "❌ No"]  # uz, ru, en

    if text in confirm_texts:
        name = user_data.get("register_name", "")
        email = user_data.get("register_email", "")
        password = user_data.get("register_password", "")
        phone = user_data.get("register_phone", "")

        tokens, user_info = await _register_user(
            message.from_user.id, name, email, password, phone,
        )
        if tokens:
            await _do_login(message, state, user_info, phone, tokens)
        else:
            await message.answer(
                get_text("error", lang),
                reply_markup=remove_keyboard,
            )
            await state.set_state(StartSection.main_menu)

    elif text in restart_texts:
        await state.update_data(
            register_name=None,
            register_email=None,
            register_password=None,
            register_phone=None,
        )
        await state.set_state(AuthFSM.waiting_name)
        await message.answer(
            get_text("register.ask_name", lang),
            reply_markup=remove_keyboard,
        )
    else:
        name = user_data.get("register_name", "—")
        email = user_data.get("register_email", "—")
        phone = user_data.get("register_phone", "—")
        await message.answer(
            get_text("register.confirm", lang, name=name, email=email, phone=phone),
            reply_markup=confirm_kb (lang),
        )


# ══════════════════════════════════════════════════════════════
# BACKEND HELPERS
# ══════════════════════════════════════════════════════════════

async def _check_phone(phone: str) -> tuple[bool, dict]:
    """Check if phone exists in DB."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                CHECK_PHONE_URL,
                json={"phone": phone},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("exists", False), data.get("user", {})
    except Exception as e:
        print(f"[CHECK PHONE ERROR] {e}")
    return False, {}


async def _check_email(email: str) -> tuple[bool, dict]:
    """Check if email exists in DB."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{CHECK_EMAIL_URL}",
                params={"email": email},
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("exists", False), data.get("user", {})
    except Exception as e:
        print(f"[CHECK EMAIL ERROR] {e}")
    return False, {}


async def _login_by_phone(telegram_id: int, phone: str, password: str = None) -> tuple[bool, dict, Optional[dict]]:
    """Login by phone. If password provided, verify it too."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {"telegram_id": telegram_id, "phone": phone}
            if password:
                payload["password"] = password
            response = await client.post(
                PHONE_LOGIN_URL,
                json=payload,
            )
            if response.status_code == 200:
                data = response.json()
                tokens = {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token"),
                }
                return True, data.get("user", {}), tokens
    except Exception as e:
        print(f"[PHONE LOGIN ERROR] {e}")
    return False, {}, None


async def _login_by_email(email: str, password: str) -> tuple[bool, dict, Optional[dict]]:
    """Login by email+password."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                EMAIL_LOGIN_URL,
                json={"email": email, "password": password},
            )
            if response.status_code == 200:
                data = response.json()
                tokens = {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token"),
                }
                return True, data.get("user", {}), tokens
    except Exception as e:
        print(f"[EMAIL LOGIN ERROR] {e}")
    return False, {}, None


async def _register_user(
    telegram_id: int, name: str, email: str, password: str, phone: str = "",
) -> tuple[Optional[dict], dict]:
    """Register new user via backend API."""
    try:
        payload = {
            "telegram_id": telegram_id,
            "full_name": name,
            "email": email,
            "password": password,
            "phone": phone,
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
    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
    return None, {}


async def _do_login(message: types.Message, state: FSMContext, user_info: dict, phone: str, tokens: Optional[dict] = None):
    """Complete login and show registered menu."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    update_data = {
        "registration_complete": True,
        "user_id": user_info.get("id"),
        "full_name": user_info.get("full_name", ""),
        "email": user_info.get("email", ""),
        "phone": user_info.get("phone", phone),
    }
    if tokens:
        update_data["access_token"] = tokens.get("access_token")
        update_data["refresh_token"] = tokens.get("refresh_token")

    await state.set_state(RegisteredSection.main_menu)
    await state.update_data(**update_data)
    await message.answer(
        get_text("login.success", lang, name=user_info.get("full_name", "")),
        reply_markup=remove_keyboard,
    )
    await message.answer(
        get_text("registered.welcome_new", lang, name=user_info.get("full_name", "")),
        reply_markup=registered_menu_kb(lang),
    )
    
    # Phase 2: Show channel join message
    if settings.CHANNEL_ID and settings.CHANNEL_USERNAME:
        await message.answer(
            f"📢 <b>Yangiliklarga a'zo bo'lish</b>\n\n"
            f"Barcha darslik yangiliklarini, taklif va eksklyuziv ta'limlarga faqat kanalda chiqadi!\n\n"
            f"🔗 <a href='https://t.me/{settings.CHANNEL_USERNAME}'>Kanalga a'zo bo'lish</a>"
        )


def _get_lang(data: dict) -> str:
    return data.get("lang", "uz")


def _parse_phone(text: str) -> Optional[str]:
    """Parse phone number from text. Returns normalized phone or None."""
    text = text.strip()
    # Preserve leading + if present
    has_plus = text.startswith('+')
    digits = re.sub(r'\D', '', text)
    # Check if it looks like a phone number (at least 9 digits)
    if len(digits) >= 9:
        if has_plus or digits.startswith('998'):
            # Already has country code or is Uzbekistan
            if not digits.startswith('+'):
                digits = '+' + digits
        else:
            # Assume Uzbek number without country code
            digits = '+998' + digits
        return digits
    return None


def _parse_email(text: str) -> Optional[str]:
    """Parse email from text."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, text):
        return text
    return None

