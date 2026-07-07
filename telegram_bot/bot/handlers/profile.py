"""Profile handlers — show profile + edit profile fields."""

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.states.registration import MenuSection, RegisteredSection
from bot.keyboards.reply import registered_menu_keyboard
from bot.keyboards.inline import registered_menu_kb
from bot.utils.i18n import get_text
from bot.config import API_BASE_URL
import httpx

router = Router()


class ProfileEditFSM(StatesGroup):
    """Profile edit FSM — field selection → new value."""
    waiting_field = State()      # Qaysi maydonni o'zgartirish
    waiting_value = State()      # Yangi qiymat


# ══════════════════════════════════════════════════════════════
# PROFILE — SHOW (via callback or reply keyboard)
# ══════════════════════════════════════════════════════════════

async def show_profile(message: types.Message, state: FSMContext, from_callback: bool = False):
    """Show user profile with email and inline keyboard."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    name = user_data.get("full_name", message.from_user.first_name or "User")
    phone = user_data.get("phone", "—")
    email = user_data.get("email", "—")
    level = user_data.get("cefr_level", "A1")
    password = user_data.get("password")

    # Determine telegram id for this user (state may store different keys)
    telegram_id = user_data.get("user_id") or user_data.get("telegram_id") or user_data.get("id") or message.from_user.id
    if telegram_id:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Use sync endpoint (no auth) to fetch user by telegram id
                resp = await client.get(f"{API_BASE_URL}/sync/user/{telegram_id}")
                if resp.status_code == 200:
                    data = resp.json()
                    email = data.get("email", email)
                    name = data.get("full_name", name)
                    phone = data.get("phone", phone)
                    level = data.get("cefr_level", level)
                    password = data.get("password", None)
                    # Update state with fresh data
                    await state.update_data(
                        email=email, full_name=name, phone=phone, cefr_level=level, password=password
                    )
        except Exception:
            pass

    # Use localized template with all required fields
    tmpl = get_text('profile.title', lang)
    text = tmpl.format(
        name=name,
        phone=phone,
        level=level,
        lang=lang.upper(),
        password=password if password else "—"
    )
    # Optionally include password display if available (user requested)
    if password:
        text += f"\n🔑 Parol: {password}"

    # Inline keyboard for Edit and Back
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    edit_text = "✏️ Tahrirlash" if lang == "uz" else ("✏️ Редактировать" if lang == "ru" else "✏️ Edit")
    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")
    builder.button(text=edit_text, callback_data="profile_edit")
    builder.button(text=back_text, callback_data="back_to_menu")
    builder.adjust(1)

    if from_callback:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "menu_profile")
async def menu_profile(callback: types.CallbackQuery, state: FSMContext):
    """Show user profile via callback."""
    await callback.message.delete()
    await show_profile(callback.message, state, from_callback=True)
    await callback.answer()


@router.message(F.text.in_([
    "👤 Profil", "👤 Профиль", "👤 Profile",
]))
async def cmd_profile(message: types.Message, state: FSMContext):
    """Show user profile via reply keyboard."""
    await show_profile(message, state, from_callback=False)


# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — FIELD SELECTION
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "profile_edit")
async def profile_edit_start(callback: types.CallbackQuery, state: FSMContext):
    """Show field selection for profile editing."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    await state.set_state(ProfileEditFSM.waiting_field)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    texts = {
        "uz": ["📝 Ism", "📧 Email", "📱 Telefon", "📊 CEFR Level", "🔑 Parol"],
        "ru": ["📝 Имя", "📧 Email", "📱 Телефон", "📊 CEFR Level", "🔑 Пароль"],
        "en": ["📝 Name", "📧 Email", "📱 Phone", "📊 CEFR Level", "🔑 Password"],
    }
    fields = ["name", "email", "phone", "cefr", "password"]
    t = texts.get(lang, texts["uz"])
    
    builder = InlineKeyboardBuilder()
    for text, field in zip(t, fields):
        builder.button(text=text, callback_data=f"edit_{field}")
    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")
    builder.button(text=back_text, callback_data="back_to_menu")
    builder.adjust(1)

    await callback.message.edit_text(
        get_text("profile.edit_prompt", lang),
        reply_markup=builder.as_markup(),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — VALUE INPUT
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("edit_"))
async def profile_edit_field(callback: types.CallbackQuery, state: FSMContext):
    """Handle field selection — prompt for new value."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    field = callback.data.split("_")[1]
    await state.update_data(editing_field=field)
    await state.set_state(ProfileEditFSM.waiting_value)

    prompts = {
        "uz": {
            "name": "Yangi ismni kiriting:",
            "email": "Yangi emailni kiriting:",
            "phone": "Yangi telefon raqamini kiriting:",
            "cefr": "Yangi CEFR levelni tanlang:",
            "password": "Yangi parolni kiriting:",
        },
        "ru": {
            "name": "Введите новое имя:",
            "email": "Введите новый email:",
            "phone": "Введите новый номер телефона:",
            "cefr": "Выберите новый CEFR level:",
            "password": "Введите новый пароль:",
        },
        "en": {
            "name": "Enter new name:",
            "email": "Enter new email:",
            "phone": "Enter new phone number:",
            "cefr": "Select new CEFR level:",
            "password": "Enter new password:",
        },
    }
    prompt = prompts.get(lang, prompts["uz"]).get(field, "Enter new value:")

    # For CEFR, show inline keyboard
    if field == "cefr":
        from bot.keyboards.inline import cefr_level_selection
        await callback.message.edit_text(prompt, reply_markup=cefr_level_selection())
    else:
        await callback.message.edit_text(prompt)

    await callback.answer()


@router.message(ProfileEditFSM.waiting_value)
async def profile_edit_value(message: types.Message, state: FSMContext):
    """Handle new value input and save to backend."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    field = user_data.get("editing_field")
    # Resolve telegram id (state keys vary between flows)
    user_id = user_data.get("user_id") or user_data.get("telegram_id") or user_data.get("id") or message.from_user.id
    new_value = message.text.strip()

    if not user_id:
        await message.answer(get_text("error", lang))
        await state.set_state(RegisteredSection.main_menu)
        return

    # Field mapping
    field_map = {
        "name": "full_name",
        "email": "email",
        "phone": "phone",
        "password": "password",
    }
    api_field = field_map.get(field, field)

    # Update via backend
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Allow password change via same endpoint — backend will hash it
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{user_id}",
                json={api_field: new_value},
            )
            if resp.status_code == 200:
                # Update local state
                await state.update_data(**{api_field: new_value})
                await message.answer(
                    get_text("profile.updated", lang, field=field),
                    reply_markup=registered_menu_keyboard(lang),
                )
            else:
                await message.answer(
                    f"❌ Xatolik: {resp.status_code}\n{resp.text}",
                    reply_markup=registered_menu_keyboard(lang),
                )
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: {str(e)}",
            reply_markup=registered_menu_keyboard(lang),
        )

    await state.set_state(RegisteredSection.main_menu)


@router.callback_query(F.data.startswith("level_"), StateFilter(ProfileEditFSM.waiting_value))
async def profile_edit_cefr(callback: types.CallbackQuery, state: FSMContext):
    """Handle CEFR level selection."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    level = callback.data.split("_")[1]
    user_id = user_data.get("user_id") or user_data.get("telegram_id") or user_data.get("id") or callback.from_user.id

    if not user_id:
        await callback.answer(get_text("error", lang))
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            access_token = user_data.get("access_token")
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{user_id}",
                json={"cefr_level": level},
            )
            if resp.status_code == 200:
                await state.update_data(cefr_level=level)
                await callback.message.edit_text(
                    f"✅ CEFR level: {level}",
                )
                await callback.message.answer(
                    get_text("main_menu", lang),
                    reply_markup=registered_menu_keyboard(lang),
                )
            else:
                await callback.message.edit_text(f"❌ Xatolik: {resp.status_code}")
    except Exception as e:
        await callback.message.edit_text(f"❌ Xatolik: {str(e)}")

    await state.set_state(RegisteredSection.main_menu)
    await callback.answer()
