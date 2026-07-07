"""Registration handler — Backend Sync API.

Kept for backward compatibility with the original registration flow.
New registration flow is handled in text.py (RegistrationFSM).
"""

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.registration import (
    RegistrationStates, RegistrationFSM, RegisteredSection,
)
from bot.keyboards.inline import cefr_level_selection
from bot.keyboards.reply import (
    registered_menu_keyboard, confirm_keyboard, remove_keyboard,
)
from bot.utils.i18n import get_text
from bot.config import settings
import httpx

router = Router()

# Backend API URL
BACKEND_URL = settings.BACKEND_URL
SYNC_USER_URL = f"{BACKEND_URL}/sync/user"


async def check_user_by_phone(phone: str, telegram_id: int) -> dict | None:
    """Check if user exists in backend DB by phone and telegram_id."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SYNC_USER_URL}/{telegram_id}",
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"[SYNC ERROR] Failed to check user: {e}")
    return None


async def sync_user_to_backend(user_data: dict) -> dict | None:
    """Sync new user to backend database."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                SYNC_USER_URL,
                json=user_data,
            )
            if response.status_code in (200, 201):
                return response.json()
            print(f"[SYNC ERROR] Backend returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[SYNC ERROR] Failed to sync user: {e}")
    return None


async def save_ai_registration_to_backend(
    phone: str,
    telegram_id: int,
    telegram_username: str | None,
    full_name: str,
    birth_date: str | None = None,
    location: str | None = None,
    occupation: str | None = None,
    cefr_level: str = "A1",
    lang: str = "uz",
) -> dict | None:
    """Save AI-collected registration data to backend."""
    user_data = {
        "telegram_id": telegram_id,
        "telegram_username": telegram_username or "",
        "phone": phone,
        "full_name": full_name,
        "birth_date": birth_date or "",
        "location": location or "",
        "occupation": occupation or "",
        "cefr_level": cefr_level,
        "lang": lang,
        "auth_provider": "telegram",
    }
    return await sync_user_to_backend(user_data)


# ─── BACKWARD COMPATIBILITY: Original flow ──────────────────

@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    """Handle language selection callback (original flow)."""
    lang = callback.data.split("_")[1]
    await state.update_data(lang=lang)
    await state.set_state(RegistrationFSM.waiting_name)

    await callback.message.edit_text(get_text("registration.ask_name", lang))
    await callback.answer()


@router.message(RegistrationStates.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    """Handle name input (original flow) — redirects to new flow."""
    name = message.text.strip()
    if len(name) < 2 or len(name) > 100:
        data = await state.get_data()
        lang = data.get("lang", "uz")
        await message.answer(get_text("registration.ask_name", lang))
        return

    await state.update_data(full_name=name)
    await state.set_state(RegistrationFSM.waiting_birthdate)

    from bot.keyboards.reply import skip_keyboard
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await message.answer(
        get_text("registration.ask_birthdate", lang),
        reply_markup=skip_keyboard(lang),
    )


@router.callback_query(F.data.startswith("level_"))
async def process_level(callback: types.CallbackQuery, state: FSMContext):
    """Handle CEFR level selection — go to confirmation step."""
    level = callback.data.split("_")[1]
    await state.update_data(cefr_level=level)
    await state.set_state(RegistrationFSM.confirmation)

    data = await state.get_data()
    lang = data.get("lang", "uz")
    name = data.get("full_name", callback.from_user.first_name or "User")
    phone = data.get("phone", "—")
    age = data.get("age", "Ko'rsatilmagan")

    await callback.message.edit_text(
        get_text("registration.confirm_title", lang,
                 name=name, phone=phone, age=str(age), level=level),
        reply_markup=confirm_keyboard(lang),
    )
    await callback.answer()

