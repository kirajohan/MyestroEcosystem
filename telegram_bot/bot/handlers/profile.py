"""Profile handlers — show profile + edit profile fields."""

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.states.registration import MenuSection, RegisteredSection
from bot.utils.i18n import get_text
from bot.config import API_BASE_URL
from bot.keyboards.reply import (
    registered_menu_kb,
    profile_kb,
    profile_edit_fields_kb,
    cefr_level_selection_with_back,
    admin_contact_kb,
)
import httpx


router = Router()


class _SafeFormatDict(dict):
    """
    Shablonda yetishmayotgan placeholder bo'lsa ham KeyError chiqmasligi uchun.
    Masalan, eski matnlarda {password} qolib ketgan bo'lsa, bo'sh qaytaradi.
    """

    def __missing__(self, key):
        return ""


class ProfileEditFSM(StatesGroup):
    """Profile edit FSM — field selection → new value."""
    waiting_field = State()      # Qaysi maydonni o'zgartirish
    waiting_value = State()      # Yangi qiymat


# ══════════════════════════════════════════════════════════════
# PROFILE — SHOW
# ══════════════════════════════════════════════════════════════
async def show_profile(message: types.Message, state: FSMContext, from_callback: bool = False):
    """Show user profile with telegram_id, phone and CEFR level."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    name = user_data.get("full_name", message.from_user.first_name or "User")
    phone = user_data.get("phone", "—")
    email = user_data.get("email", "—")
    level = user_data.get("cefr_level", "A1")
    password = user_data.get("password_hash", user_data.get("password", "—"))

    telegram_id = message.from_user.id

    # Backend'dan yangi ma'lumotlarni olish
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE_URL}/sync/user/{telegram_id}")
            if resp.status_code == 200:
                data = resp.json()

                email = data.get("email", email)
                name = data.get("full_name", name)
                phone = data.get("phone", phone)
                level = data.get("cefr_level", level)
                telegram_id = data.get("telegram_id", telegram_id)
                # 🔑 password_hash ni olish (DB dagi nom)
                password = data.get("password_hash", data.get("password", password))

                await state.update_data(
                    email=email,
                    full_name=name,
                    phone=phone,
                    cefr_level=level,
                    telegram_id=telegram_id,
                    password=password,
                    password_hash=password,
                )
    except Exception:
        pass

    tmpl = get_text("profile.title", lang)

    # 🔑 Parol borligini ko'rsatish (lekin haqiqiy parolni emas)
    password_status = "✅ O'rnatilgan" if password and password != "—" else "***"

    values = _SafeFormatDict(
        name=name,
        phone=phone,
        email=email,
        level=level,
        lang=lang.upper(),
        telegram_id=telegram_id,
        password=password_status,  # <--- Bu yerda status ko'rsatiladi
    )

    try:
        text = tmpl.format_map(values)
    except ValueError:
        text = f"👤 {name}\n📞 {phone}\n📊 {level}\n🔑 Parol: {password}"

    text += f"\n\n🆔 Telegram ID: <code>{telegram_id}</code>"

    keyboard = profile_kb(lang)

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(F.text.in_([
    "👤 Profil", "👤 Профиль", "👤 Profile",
]))
async def cmd_profile(message: types.Message, state: FSMContext):
    """Show user profile via reply keyboard."""
    await show_profile(message, state, from_callback=False)


@router.message(
    StateFilter(RegisteredSection.main_menu),
    F.text.in_(["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"])
)
async def menu_profile(message: types.Message, state: FSMContext):
    """Back button from profile screen → registered menu."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    await state.set_state(RegisteredSection.main_menu)
    await message.answer(
        get_text("main_menu", lang),
        reply_markup=registered_menu_kb(lang)
    )


# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — START
# ══════════════════════════════════════════════════════════════

@router.message(
    StateFilter(RegisteredSection.main_menu),
    F.text.in_(["✏️ Tahrirlash", "✏️ Редактировать", "✏️ Edit"])
)
async def profile_edit_start(message: types.Message, state: FSMContext):
    """Show field selection for profile editing using reply buttons."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    await state.set_state(ProfileEditFSM.waiting_field)

    await message.answer(
        get_text("profile.edit_prompt", lang),
        reply_markup=profile_edit_fields_kb(lang)
    )


# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — FIELD SELECTION
# ══════════════════════════════════════════════════════════════

@router.message(ProfileEditFSM.waiting_field)
async def profile_edit_field(message: types.Message, state: FSMContext):
    """Handle field selection — prompt for new value."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    text = message.text.strip() if message.text else ""

    back_texts = ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"]

    name_texts = ["📝 Ism", "📝 Имя", "📝 Name"]
    cefr_texts = ["📊 CEFR Level"]

    # Back
    if text in back_texts:
        await state.set_state(RegisteredSection.main_menu)
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang)
        )
        return

    # Field tanlash
    if text in name_texts:
        field = "name"
    elif text in cefr_texts:
        field = "cefr"
    else:
        # Noto'g'ri bosilganda field selection ni qayta ko'rsatamiz
        await message.answer(
            get_text("profile.edit_prompt", lang),
            reply_markup=profile_edit_fields_kb(lang)
        )
        return

    await state.update_data(editing_field=field)
    await state.set_state(ProfileEditFSM.waiting_value)

    prompts = {
        "uz": {
            "name": "Yangi ismni kiriting:",
            "cefr": "Yangi CEFR levelni tanlang:",
        },
        "ru": {
            "name": "Введите новое имя:",
            "cefr": "Выберите новый CEFR level:",
        },
        "en": {
            "name": "Enter new name:",
            "cefr": "Select new CEFR level:",
        },
    }

    prompt = prompts.get(lang, prompts["uz"]).get(field, "Enter new value:")

    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")

    # CEFR uchun level tugmalarini reply keyboard sifatida ko'rsatamiz
    if field == "cefr":
        await message.answer(
            prompt,
            reply_markup=cefr_level_selection_with_back(lang)
        )
        return

    # Name uchun faqat Back tugmasi bilan keyboard
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=back_text)],
        ],
        resize_keyboard=True,
    )

    await message.answer(
        prompt,
        reply_markup=keyboard
    )

# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — PASSWORD CHANGE
# ══════════════════════════════════════════════════════════════

class PasswordChangeFSM(StatesGroup):
    waiting_new_password = State()
    confirm_password = State()


@router.message(
    StateFilter(RegisteredSection.main_menu),
    F.text.in_(["🔑 Parolni o'zgartirish", "🔑 Сменить пароль", "🔑 Change password"])
)
async def password_change_start(message: types.Message, state: FSMContext):
    """Start password change process."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    await state.set_state(PasswordChangeFSM.waiting_new_password)

    prompts = {
        "uz": "🔑 Yangi parolni kiriting (kamida 6 belgi):",
        "ru": "🔑 Введите новый пароль (минимум 6 символов):",
        "en": "🔑 Enter new password (minimum 6 characters):",
    }

    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=back_text)]],
        resize_keyboard=True,
    )

    await message.answer(
        prompts.get(lang, prompts["uz"]),
        reply_markup=keyboard
    )


@router.message(PasswordChangeFSM.waiting_new_password)
async def password_change_input(message: types.Message, state: FSMContext):
    """Handle new password input."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    new_password = message.text.strip()

    back_texts = ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"]

    if new_password in back_texts or new_password.startswith("⬅️"):
        await state.set_state(RegisteredSection.main_menu)
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang)
        )
        return

    # Validatsiya
    if len(new_password) < 6:
        prompts = {
            "uz": "❌ Parol kamida 6 belgidan iborat bo'lishi kerak. Qayta kiriting:",
            "ru": "❌ Пароль должен быть минимум 6 символов. Введите снова:",
            "en": "❌ Password must be at least 6 characters. Enter again:",
        }
        await message.answer(prompts.get(lang, prompts["uz"]))
        return

    # Parolni tasdiqlash
    await state.update_data(new_password=new_password)
    await state.set_state(PasswordChangeFSM.confirm_password)

    prompts = {
        "uz": "🔑 Parolni tasdiqlang (qayta kiriting):",
        "ru": "🔑 Подтвердите пароль (введите снова):",
        "en": "🔑 Confirm password (enter again):",
    }

    await message.answer(prompts.get(lang, prompts["uz"]))


@router.message(PasswordChangeFSM.confirm_password)
async def password_change_confirm(message: types.Message, state: FSMContext):
    """Confirm and save new password."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    new_password = user_data.get("new_password")
    confirm_password = message.text.strip()

    back_texts = ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"]

    if confirm_password in back_texts or confirm_password.startswith("⬅️"):
        await state.set_state(RegisteredSection.main_menu)
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang)
        )
        return

    if new_password != confirm_password:
        prompts = {
            "uz": "❌ Parollar mos kelmadi. Qaytadan boshlang.",
            "ru": "❌ Пароли не совпадают. Начните заново.",
            "en": "❌ Passwords do not match. Start over.",
        }
        await message.answer(
            prompts.get(lang, prompts["uz"]),
            reply_markup=registered_menu_kb(lang)
        )
        await state.set_state(RegisteredSection.main_menu)
        return

    # Backend ga yangi parolni yuborish
    telegram_id = message.from_user.id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{telegram_id}",
                json={"password": new_password},
            )

            if resp.status_code == 200:
                prompts = {
                    "uz": "✅ Parol muvaffaqiyatli o'zgartirildi!",
                    "ru": "✅ Пароль успешно изменен!",
                    "en": "✅ Password successfully changed!",
                }
                await message.answer(
                    prompts.get(lang, prompts["uz"]),
                    reply_markup=registered_menu_kb(lang)
                )
            else:
                await message.answer(
                    f"❌ Xatolik: {resp.status_code}",
                    reply_markup=registered_menu_kb(lang)
                )
    except Exception as e:
        await message.answer(
            f"❌ Xatolik: {str(e)}",
            reply_markup=registered_menu_kb(lang)
        )

    await state.set_state(RegisteredSection.main_menu)\

# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — CEFR LEVEL SAVE
# ══════════════════════════════════════════════════════════════

@router.message(
    ProfileEditFSM.waiting_value,
    F.text.in_(["A0", "A1", "A2", "B1", "B2", "C1", "C2"])
)
async def profile_edit_cefr(message: types.Message, state: FSMContext):
    """Handle CEFR level selection via reply keyboard."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    level = message.text.strip().upper()
    telegram_id = message.from_user.id

    if not telegram_id:
        await message.answer(get_text("error", lang))
        await state.set_state(RegisteredSection.main_menu)
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{telegram_id}",
                json={"cefr_level": level},
            )

            if resp.status_code == 200:
                await state.update_data(
                    cefr_level=level,
                    editing_field=None,
                )

                await state.set_state(RegisteredSection.main_menu)

                await message.answer(
                    f"✅ CEFR level: {level}",
                    reply_markup=registered_menu_kb(lang)
                )
            else:
                await state.set_state(RegisteredSection.main_menu)

                await message.answer(
                    f"❌ Xatolik: {str(resp.status_code)}\n{resp.text}",
                    reply_markup=registered_menu_kb(lang)
                )
    except Exception as e:
        await state.set_state(RegisteredSection.main_menu)

        await message.answer(
            f"❌ Xatolik: {str(e)}",
            reply_markup=registered_menu_kb(lang)
        )


# ══════════════════════════════════════════════════════════════
# PROFILE EDIT — VALUE INPUT
# ══════════════════════════════════════════════════════════════

@router.message(ProfileEditFSM.waiting_value)
async def profile_edit_value(message: types.Message, state: FSMContext):
    """Handle new value input and save to backend."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    field = user_data.get("editing_field")

    telegram_id = message.from_user.id
    new_value = message.text.strip() if message.text else ""

    back_texts = ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"]

    # Back
    if new_value in back_texts or new_value.startswith("⬅️"):
        await state.update_data(editing_field=None)
        await state.set_state(RegisteredSection.main_menu)

        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang)
        )
        return

    if not telegram_id:
        await message.answer(get_text("error", lang))
        await state.set_state(RegisteredSection.main_menu)
        return

    # Agar field cefr bo'lsa va noto'g'ri qiymat kiritilgan bo'lsa
    if field == "cefr":
        await message.answer(
            get_text("register.invalid_level", lang),
            reply_markup=cefr_level_selection_with_back(lang)
        )
        return

    # Field mapping
    # password olib tashlandi. Hozir faqat name ruxsat etiladi.
    field_map = {
        "name": "full_name",
    }

    api_field = field_map.get(field)

    # Noto'g'ri yoki eski field bo'lsa, asosiy menyuga qaytaramiz
    if not api_field:
        await state.update_data(editing_field=None)
        await state.set_state(RegisteredSection.main_menu)

        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang)
        )
        return

    # Name uchun validatsiya
    if field == "name":
        if len(new_value) < 2 or len(new_value) > 100:
            back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")

            keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text=back_text)],
                ],
                resize_keyboard=True,
            )

            await message.answer(
                get_text("register.invalid_name", lang),
                reply_markup=keyboard
            )
            return

    # Update via backend
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/user/{telegram_id}",
                json={api_field: new_value},
            )

            if resp.status_code == 200:
                # Update local state
                await state.update_data(**{api_field: new_value})
                await state.update_data(editing_field=None)

                await state.set_state(RegisteredSection.main_menu)

                # Agar get_text kwargs qabul qilmasa, TypeError chiqmasligi uchun fallback
                try:
                    updated_text = get_text("profile.updated", lang, field=field)
                except TypeError:
                    updated_text = get_text("profile.updated", lang)

                await message.answer(
                    updated_text,
                    reply_markup=registered_menu_kb(lang),
                )
            else:
                await state.set_state(RegisteredSection.main_menu)

                await message.answer(
                    f"❌ Xatolik: {str(resp.status_code)}\n{resp.text}",
                    reply_markup=registered_menu_kb(lang),
                )
    except Exception as e:
        await state.set_state(RegisteredSection.main_menu)

        await message.answer(
            f"❌ Xatolik: {str(e)}",
            reply_markup=registered_menu_kb(lang),
        )