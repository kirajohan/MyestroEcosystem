"""Registration handler — phone → name → CEFR level → confirmation → DB save.

Flow:
1. User presses Register → contact request
2. Phone contact validated
3. Name input
4. CEFR level selection (inline + text)
5. Confirmation
6. Save to backend API → show registered menu
"""

import httpx
from typing import Optional
from aiogram.filters import StateFilter, Command, or_f
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.states.registration import RegistrationFSM, StartSection, RegisteredSection
from bot.keyboards.reply import (
    contact_request_keyboard,
    registered_menu_kb,
    confirm_kb as confirm_reply_kb,
    main_menu,
)
from bot.keyboards.inline import cefr_level_selection
from bot.utils.i18n import get_text
from bot.config import settings, API_BASE_URL

router = Router()

# Backend API URL for registration
REGISTER_INIT_URL = f"{settings.API_BASE_URL}/api/auth/register"

# ==============================================================================
# 1-BOSQICH: REGISTER TUGMASI BOSILGANDA -> PHONE SO'RASH
# ==============================================================================
from bot.states.registrations_filter import IsNotRegistered

@router.message(
    IsNotRegistered(),
    Command("register"),
    F.text.in_(["📝 Register", "📝 Регистрация", "📝 Register"]),
)
async def start_registration(message: types.Message, state: FSMContext):
    """Register — ONLY UNREGISTERED users."""
    # ... mavjud kod
    pass
    """Foydalanuvchi Ro'yxatdan o'tish tugmasini bossa, kontakt yuborishni so'raydi."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    registration_complete = user_data.get("registration_complete", False)

    # ✅ TUZATILDI: "Orqaga" uchun foydalanuvchi qayerdan kelganini
    # state o'zgarishidan OLDIN aniqlab saqlaymiz.
    current_state = await state.get_state()

    registered_state_name = getattr(
        RegisteredSection.main_menu,
        "state_name",
        "RegisteredSection:main_menu"
    )
    registered_prefix = registered_state_name.split(":")[0]

    came_from_registered = bool(
        current_state and current_state.startswith(registered_prefix)
    )

    is_registered_source = (
        registration_complete
        or bool(user_data.get("user_id"))
        or came_from_registered
    )

    await state.update_data(
        started_from="registered" if is_registered_source else "unregistered"
    )

    # 1. AGAR FOYDALANUVCHI ALLAQACHON RO'YXATDAN O'TGAN BO'LSA:
    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
        return await message.answer(
            get_text("register.already_registered", lang),
            reply_markup=registered_menu_kb(lang)
        )

    # Ro'yxatdan o'tmagan bo'lsa, jarayonni boshlaymiz
    await state.set_state(RegistrationFSM.waiting_phone)
    await message.answer(
        get_text("register.ask_phone", lang),
        reply_markup=contact_request_keyboard(lang)  # request_contact=True va Orqaga tugmasi
    )
    pass
# ==============================================================================
# 2-BOSQICH: TELEFON KONTAKTINI QABUL QILISH VA XAVFSIZLIK TEKSHIRUVI
# ==============================================================================
@router.message(RegistrationFSM.waiting_phone)
async def handle_phone(message: types.Message, state: FSMContext):
    """Telegram Contact obyektini qabul qiladi va ID tengligini tekshiradi."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    registration_complete = user_data.get("registration_complete", False)
    started_from = user_data.get("started_from", "unregistered")  # ✅ started_from o'qish

    # 1. AGAR FOYDALANUVCHI TUGMANI BOSMAY, MATN YOZIB YUBORGAN BO'LSA:
    if not message.contact:
        # Foydalanuvchi "⬅️ Orqaga" tugmasini bosgan bo'lsa:
        if message.text and (
            message.text.startswith("⬅️")
            or message.text in ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"]
        ):

            # ✅ TUZATILDI:
            # Agar user registered bo'lsa -> registered_menu_kb
            # Agar unregistered bo'lsa -> main_menu
            is_registered_source = (
                started_from == "registered"
                or registration_complete
                or bool(user_data.get("user_id"))
            )

            if is_registered_source:
                await state.set_state(RegisteredSection.main_menu)
                menu = registered_menu_kb(lang)
            else:
                await state.set_state(StartSection.main_menu)
                menu = main_menu(lang)

            # Toza boshlash uchun vaqtinchalik register maydonlarini tozalab qo'yamiz
            await state.update_data(
                register_phone=None,
                register_name=None,
                register_level=None,
            )

            await message.answer(
                get_text("register.cancelled", lang),
                reply_markup=menu
            )
            return

        # Shunchaki qo'lda text yozib yuborgan bo'lsa (masalan: +998901234567)
        await message.answer(
            get_text("register.must_use_contact_button", lang),
            reply_markup=contact_request_keyboard(lang)
        )
        return

    # 2. XAVFSIZLIK TEKSHIRUVI: Yuborilgan kontakt ushbu foydalanuvchining o'zinikimi?
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            get_text("register.not_your_contact", lang),  # "⚠️ Bu sizning raqamingiz emas!..."
            reply_markup=contact_request_keyboard(lang)
        )
        return

    # Telefon raqamini formatlab saqlaymiz
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"

    await state.update_data(register_phone=phone)
    await state.set_state(RegistrationFSM.waiting_name)

    # Keyingi bosqich: Ism so'rash
    await message.answer(
        get_text("register.ask_name", lang),
        reply_markup=types.ReplyKeyboardRemove()  # Tugmani olib tashlaymiz
    )
# ==============================================================================
# 3-BOSQICH: ISMNI QABUL QILISH -> LEVEL SO'RASH
# ==============================================================================
@router.message(RegistrationFSM.waiting_name)
async def handle_name(message: types.Message, state: FSMContext):
    """Ismni qabul qiladi va Ingliz tili darajasini (Level) so'raydi."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    name = message.text.strip() if message.text else ""

    if len(name) < 2 or len(name) > 100:
        await message.answer(get_text("register.invalid_name", lang))
        return

    await state.update_data(register_name=name)
    await state.set_state(RegistrationFSM.waiting_level)

    # Keyingi bosqich: Level (Daraja) tanlash tugmalarini chiqarish
    await message.answer(
        get_text("register.ask_level", lang),
        reply_markup=cefr_level_selection()  # A1, A2, B1, B2, C1, C2 tugmalari
    )


# ==============================================================================
# 4-BOSQICH: LEVEL DARAJANING QABUL QILINISHI (Inline va Text uchun)
# ==============================================================================
@router.callback_query(RegistrationFSM.waiting_level, F.data.startswith("level_"))
async def handle_level_callback(callback: types.CallbackQuery, state: FSMContext):
    """Inline tugma orqali Level tanlanganda."""
    level = callback.data.split("_")[1]  # masalan: level_B2 -> B2
    await callback.answer()
    await _save_level_and_ask_confirm(callback.message, state, level, is_edit=True)


@router.message(RegistrationFSM.waiting_level)
async def handle_level_text(message: types.Message, state: FSMContext):
    """Foydalanuvchi matn shaklida darajani yozganda (Masalan: B2)."""
    level = message.text.strip().upper() if message.text else ""
    valid_levels = ["A0", "A1", "A2", "B1", "B2", "C1", "C2"]

    if level not in valid_levels:
        user_data = await state.get_data()
        lang = user_data.get("lang", "uz")
        await message.answer(
            get_text("register.invalid_level", lang),
            reply_markup=cefr_level_selection()
        )
        return

    await _save_level_and_ask_confirm(message, state, level, is_edit=False)


async def _save_level_and_ask_confirm(message: types.Message, state: FSMContext, level: str, is_edit: bool = False):
    """Level'ni saqlab, yakuniy tasdiqlash oynasini ko'rsatuvchi yordamchi funksiya."""
    await state.update_data(register_level=level)
    await state.set_state(RegistrationFSM.waiting_confirmation)

    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    phone = user_data.get("register_phone", "—")
    name = user_data.get("register_name", "—")

    text = get_text("register.confirm_info", lang, name=name, phone=phone, level=level)
    kb = confirm_reply_kb(lang)  # ✅ Ha / ❌ Yo'q REPLY tugmalari

    if is_edit:
        # Telegram API cheklovi tufayli: Inline message ga ReplyKeyboard qo'yib bo'lmaydi,
        # shuning uchun eski inline xabarni o'chirib, yangi reply message yuboramiz.
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


# ==============================================================================
# 5-BOSQICH: CONFIRMATION (TASDIQLASH) -> DB GA SAQLASH -> registered_menu_kb
# ==============================================================================
@router.message(RegistrationFSM.waiting_confirmation)
async def handle_confirmation(message: types.Message, state: FSMContext):
    """Ma'lumotlarni tasdiqlaydi, DB ga saqlaydi va Asosiy Menyoga o'tkazadi."""
    text = message.text.strip() if message.text else ""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    confirm_texts = ["✅ Ha", "✅ Да", "✅ Yes"]
    restart_texts = ["❌ Yo'q", "❌ Нет", "❌ No"]

    if text in confirm_texts:
        name = user_data.get("register_name", "")
        phone = user_data.get("register_phone", "")
        level = user_data.get("register_level", "")
        telegram_id = message.from_user.id

        # Backend API / DB ga saqlash so'rovi
        success, user_info = await register_user_in_db(
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            level=level,
            lang=lang
        )

        if success:
            # Ro'yxatdan o'tish muvaffaqiyatli — canonical state keys saqlanadi
            await state.update_data(
                registration_complete=True,
                user_id=user_info.get("id") or telegram_id,
                full_name=user_info.get("full_name") or name,
                phone=user_info.get("phone") or phone,
                cefr_level=user_info.get("cefr_level") or level,
                lang=lang,
            )
            await state.set_state(RegisteredSection.main_menu)

            await message.answer(
                get_text("register.success_welcome", lang),
                reply_markup=registered_menu_kb(lang)  # Ro'yxatdan o'tganlar menyusi!
            )
        else:
            await message.answer(
                get_text("error", lang),
                reply_markup=types.ReplyKeyboardRemove()
            )

    elif text in restart_texts:
        # Rad etilgan taqdirda ma'lumotlar tozalanadi va qayta telefon so'rash bosqichiga qaytariladi
        await state.update_data(
            register_name=None,
            register_phone=None,
            register_level=None
        )
        await state.set_state(RegistrationFSM.waiting_phone)
        await message.answer(
            get_text("register.ask_phone", lang),
            reply_markup=contact_request_keyboard(lang)
        )
    else:
        await message.answer(
            get_text("register.choose_yes_or_no", lang),
            reply_markup=confirm_reply_kb(lang)
        )


# ==============================================================================
# BACKEND HELPERS
# ==============================================================================


async def _register_user(
    telegram_id: int,
    name: str,
    email: str,
    password: str,
    phone: str = "",
    level: str = "",
    lang: str = "uz",
) -> tuple[Optional[dict], dict]:
    """Register new user via backend API."""
    try:
        payload = {
            "telegram_id": telegram_id,
            "full_name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "cefr_level": level,
            "lang": lang,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                REGISTER_INIT_URL,
                json=payload,
            )
            if response.status_code in (200, 201):
                data = response.json()
                # Backend returns: {"success": bool, "user": {...}}
                user_info = data.get("user", {})
                return data.get("success"), user_info
    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
    return False, {}


async def register_user_in_db(
    telegram_id: int,
    name: str,
    phone: str,
    level: str,
    lang: str = "uz"
) -> tuple[bool, dict]:
    """
    Handler tomonidan ishlatiladigan helper funksiya.
    Email/Parol telegram foydalanuvchisidan so'ralmagani sababli avtomatik generatsiya qilinadi.
    Muvaffaqiyatli o'tsa (True, user_info), aks holda (False, {}) qaytaradi.
    """
    # Backend email va password talab qilsa, zaxira qiymatlar yaratiladi:
    email = f"user_{telegram_id}@myestro.local"
    password = f"tg_pass_{telegram_id}"

    return await _register_user(
        telegram_id=telegram_id,
        name=name,
        email=email,
        password=password,
        phone=phone,
        level=level,
        lang=lang,
    )