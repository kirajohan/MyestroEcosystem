# bot/handlers/profile.py
"""Profile handlers — show profile + edit profile fields with colored keyboards."""

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from bot.states.registration import MenuSection, RegisteredSection
from bot.keyboards.inline import main_menu_kb
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
    """Show user profile with colored inline keyboard."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    name = user_data.get("full_name", message.from_user.first_name or "User")
    phone = user_data.get("phone", "—")
    email = user_data.get("email", "—")
    level = user_data.get("cefr_level", "A1")

    # Determine telegram id for this user
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
                    # Update state with fresh data
                    await state.update_data(
                        email=email, full_name=name, phone=phone, cefr_level=level
                    )
        except Exception as e:
            print(f"[PROFILE FETCH ERROR] {e}")

    # Build profile text
    profile_texts = {
        "uz": (
            f"👤 <b>Mening Profilim</b>\n\n"
            f"📝 <b>Ism:</b> {name}\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"📊 <b>CEFR Level:</b> {level}\n"
            f"🌐 <b>Til:</b> {lang.upper()}"
        ),
        "ru": (
            f"👤 <b>Мой профиль</b>\n\n"
            f"📝 <b>Имя:</b> {name}\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📱 <b>Телефон:</b> {phone}\n"
            f"📊 <b>CEFR Level:</b> {level}\n"
            f"🌐 <b>Язык:</b> {lang.upper()}"
        ),
        "en": (
            f"👤 <b>My Profile</b>\n\n"
            f"📝 <b>Name:</b> {name}\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📱 <b>Phone:</b> {phone}\n"
            f"📊 <b>CEFR Level:</b> {level}\n"
            f"🌐 <b>Language:</b> {lang.upper()}"
        )
    }
    
    text = profile_texts.get(lang, profile_texts["uz"])

    # Inline keyboard — Edit + Back
    builder = InlineKeyboardBuilder()
    
    edit_texts = {"uz": "✏️ Tahrirlash", "ru": "✏️ Редактировать", "en": "✏️ Edit"}
    back_texts = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
    
    builder.add(
        InlineKeyboardButton(
            text=edit_texts.get(lang, edit_texts["uz"]),
            callback_data="profile_edit",
        ),
        InlineKeyboardButton(
            text=back_texts.get(lang, back_texts["uz"]),
            callback_data="back_to_menu",
        ),
    )
    builder.adjust(1)

    if from_callback:
        await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "menu_profile")
async def menu_profile(callback: types.CallbackQuery, state: FSMContext):
    """Show user profile via callback."""
    await show_profile(callback.message, state, from_callback=True)
    await callback.answer()


@router.message(F.text.in_([
    "👤 Profil", "👤 Профиль", "👤 Profile",
]))
async def cmd_profile(message: types.Message, state: FSMContext):
    """Show user profile via reply keyboard."""
    await show_profile(message, state, from_callback=False)


# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — FIELD SELECTION (with colored buttons)
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "profile_edit")
async def profile_edit_start(callback: types.CallbackQuery, state: FSMContext):
    """Show field selection for profile editing — colored buttons."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    await state.set_state(ProfileEditFSM.waiting_field)

    builder = InlineKeyboardBuilder()
    
    # Field options
    field_options = {
        "uz": [
            ("📝 Ism", "edit_name"),
            ("📧 Email", "edit_email"),
            ("📱 Telefon", "edit_phone"),
            ("📊 CEFR Level", "edit_cefr"),
            ("⬅️ Orqaga", "back_to_menu"),
        ],
        "ru": [
            ("📝 Имя", "edit_name"),
            ("📧 Email", "edit_email"),
            ("📱 Телефон", "edit_phone"),
            ("📊 CEFR Level", "edit_cefr"),
            ("⬅️ Назад", "back_to_menu"),
        ],
        "en": [
            ("📝 Name", "edit_name"),
            ("📧 Email", "edit_email"),
            ("📱 Phone", "edit_phone"),
            ("📊 CEFR Level", "edit_cefr"),
            ("⬅️ Back", "back_to_menu"),
        ],
    }
    
    options = field_options.get(lang, field_options["uz"])
    
    for text, callback_data in options:
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
            )
        )
    
    builder.adjust(1)

    prompt_texts = {
        "uz": "🎯 Qaysi maydonni tahrirlash kerak?",
        "ru": "🎯 Какое поле вы хотите редактировать?",
        "en": "🎯 Which field would you like to edit?",
    }

    await callback.message.edit_text(
        prompt_texts.get(lang, prompt_texts["uz"]),
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
            "name": "📝 Yangi ismni kiriting:",
            "email": "📧 Yangi emailni kiriting:",
            "phone": "📱 Yangi telefon raqamini kiriting:",
            "cefr": "📊 Yangi CEFR levelni tanlang:",
        },
        "ru": {
            "name": "📝 Введите новое имя:",
            "email": "📧 Введите новый email:",
            "phone": "📱 Введите новый номер телефона:",
            "cefr": "📊 Выберите новый CEFR level:",
        },
        "en": {
            "name": "📝 Enter new name:",
            "email": "📧 Enter new email:",
            "phone": "📱 Enter new phone number:",
            "cefr": "📊 Select new CEFR level:",
        },
    }
    prompt = prompts.get(lang, prompts["uz"]).get(field, "Enter new value:")

    # For CEFR, show inline keyboard with colored buttons
    if field == "cefr":
        await callback.message.edit_text(
            prompt,
            reply_markup=_cefr_selection_keyboard(lang),
        )
    else:
        await callback.message.edit_text(prompt)

    await callback.answer()


@router.message(ProfileEditFSM.waiting_value)
async def profile_edit_value(message: types.Message, state: FSMContext):
    """Handle new value input and save to backend."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    field = user_data.get("editing_field")
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
    }
    api_field = field_map.get(field, field)

    # Update via backend
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{user_id}",
                json={api_field: new_value},
            )
            if resp.status_code == 200:
                # Update local state
                await state.update_data(**{api_field: new_value})
                
                success_texts = {
                    "uz": f"✅ {field.upper()} yangilandi!",
                    "ru": f"✅ {field.upper()} обновлено!",
                    "en": f"✅ {field.upper()} updated!",
                }
                
                await message.answer(
                    success_texts.get(lang, success_texts["uz"]),
                    reply_markup=main_menu_kb(lang),
                )
            else:
                error_msg = f"❌ Xatolik: {resp.status_code}\n{resp.text}"
                await message.answer(
                    error_msg,
                    reply_markup=main_menu_kb(lang),
                )
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: {str(e)}",
            reply_markup=main_menu_kb(lang),
        )

    await state.set_state(RegisteredSection.main_menu)


@router.callback_query(F.data.startswith("level_"), StateFilter(ProfileEditFSM.waiting_value))
async def profile_edit_cefr(callback: types.CallbackQuery, state: FSMContext):
    """Handle CEFR level selection."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    level = callback.data.split("_")[1].upper()
    user_id = user_data.get("user_id") or user_data.get("telegram_id") or user_data.get("id") or callback.from_user.id

    if not user_id:
        await callback.answer(get_text("error", lang))
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{user_id}",
                json={"cefr_level": level},
            )
            if resp.status_code == 200:
                await state.update_data(cefr_level=level)
                
                success_texts = {
                    "uz": f"✅ CEFR level: <b>{level}</b>",
                    "ru": f"✅ CEFR уровень: <b>{level}</b>",
                    "en": f"✅ CEFR level: <b>{level}</b>",
                }
                
                await callback.message.edit_text(
                    success_texts.get(lang, success_texts["uz"]),
                    parse_mode="HTML",
                )
                await callback.message.answer(
                    get_text("main_menu", lang),
                    reply_markup=main_menu_kb(lang),
                )
            else:
                await callback.message.edit_text(f"❌ Xatolik: {resp.status_code}")
    except Exception as e:
        await callback.message.edit_text(f"❌ Xatolik: {str(e)}")

    await state.set_state(RegisteredSection.main_menu)
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _cefr_selection_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """CEFR level selection — inline keyboard."""
    builder = InlineKeyboardBuilder()
    
    levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    
    for level in levels:
        builder.add(
            InlineKeyboardButton(
                text=f"📊 {level}",
                callback_data=f"level_{level.lower()}",
            )
        )
    
    # Cancel button
    cancel_texts = {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "en": "❌ Cancel"}
    builder.add(
        InlineKeyboardButton(
            text=cancel_texts.get(lang, cancel_texts["uz"]),
            callback_data="back_to_menu",
        )
    )
    
    builder.adjust(3, 3, 1)  # 3-3-1 layout
    return builder.as_markup()
