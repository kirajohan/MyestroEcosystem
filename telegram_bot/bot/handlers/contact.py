"""Contact handler — phone number sharing for AuthFSM.

Flow:
1. User shares phone number (contact)
2. Check DB by phone
3. If found → auto-login
4. If NOT found → Registration (AuthFSM)
"""

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from typing import Optional
from bot.states.registration import AuthFSM, RegisteredSection, StartSection
from bot.keyboards.reply import remove_keyboard
from bot.keyboards.inline import main_menu_kb
from bot.utils.i18n import get_text
from bot.config import settings
import httpx

router = Router()

PHONE_LOGIN_URL = f"{settings.API_BASE_URL}/auth/phone-login"
CHECK_PHONE_URL = f"{settings.API_BASE_URL}/auth/check-phone"


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


async def _login_by_phone(telegram_id: int, phone: str) -> tuple[bool, dict, Optional[dict]]:
    """Login by phone (auto-login via contact share)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                PHONE_LOGIN_URL,
                json={"telegram_id": telegram_id, "phone": phone},
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
        reply_markup=main_menu_kb(lang=lang),
    )


@router.message(F.contact, StateFilter(AuthFSM.requesting_contact))
async def handle_contact(message: types.Message, state: FSMContext):
    """Handle contact share — check DB, login or register."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # ═══════════════════════════════════════════════════════════
    # SECURITY CHECK 1: Block forwarded contacts
    # ═══════════════════════════════════════════════════════════
    if message.forward_origin:
        await message.answer(
            get_text("contact.forwarded", lang),
            reply_markup=remove_keyboard,
        )
        await state.set_state(StartSection.main_menu)
        return

    # ═══════════════════════════════════════════════════════════
    # SECURITY CHECK 2: Only own contact allowed
    # ═══════════════════════════════════════════════════════════
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            get_text("contact.not_own", lang),
            reply_markup=remove_keyboard,
        )
        await state.set_state(StartSection.main_menu)
        return

    # ═══════════════════════════════════════════════════════════
    # SECURITY CHECK 3: State session validation
    # ═══════════════════════════════════════════════════════════
    stored_telegram_id = user_data.get("telegram_id")
    if stored_telegram_id and stored_telegram_id != message.from_user.id:
        # state.clear() dan keyin yangi state o'rnatamiz (None state'ga tushib qolishining oldini olish)
        await state.clear()
        await state.set_state(StartSection.main_menu)
        await state.update_data(lang=lang)
        await message.answer(
            get_text("contact.session_mismatch", lang),
            reply_markup=remove_keyboard,
        )
        return

    phone = message.contact.phone_number
    telegram_id = message.from_user.id

    # ═══════════════════════════════════════════════════════════
    # SECURITY CHECK 4: Phone number validation
    # ═══════════════════════════════════════════════════════════
    if not phone or len(phone) < 9:
        await message.answer(
            get_text("contact.invalid_phone", lang),
            reply_markup=remove_keyboard,
        )
        await state.set_state(StartSection.main_menu)
        return

    # Check DB by phone
    exists, user_info = await _check_phone(phone)
    
    if exists:
        # Auto-login
        success, login_info, tokens = await _login_by_phone(telegram_id, phone)
        if success:
            await _do_login(message, state, login_info, phone, tokens)
        else:
            # Phone found but login failed (e.g., telegram_id mismatch)
            await message.answer(
                get_text("auth.phone_found_but_login_failed", lang),
                reply_markup=remove_keyboard,
            )
            await state.set_state(StartSection.main_menu)
    else:
        # Not found → start registration with phone
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
