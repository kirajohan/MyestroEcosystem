from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from bot.states.registration import RegistrationFSM
from bot.keyboards.reply import (
    contact_request_keyboard,
    registered_menu_kb,
    confirm_kb as confirm_reply_kb,
)
from bot.keyboards.inline  import (
    cefr_level_selection,
    confirm_kb,
)
from bot.utils.i18n import get_text
# Backend API orqali ro'yxatdan o'tkazish funksiyasi

router = Router()

# ==============================================================================
# 1-BOSQICH: REGISTER TUGMASI BOSILGANDA -> PHONE SO'RASH
# ==============================================================================
@router.message(F.text.in_(["📝 Register", "📝 Ro'yxatdan o'tish", "📝 Регистрация"]))
async def start_registration(message: types.Message, state: FSMContext):
    """Foydalanuvchi Ro'yxatdan o'tish tugmasini bossa, kontakt yuborishni so'raydi."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")
    
    await state.set_state(RegistrationFSM.waiting_phone)
    await message.answer(
        get_text("register.ask_phone", lang),
        reply_markup=contact_request_keyboard(lang)  # request_contact=True tugmasi
    )

# ==============================================================================
# 2-BOSQICH: TELEFON KONTAKTINI QABUL QILISH VA XAVFSIZLIK TEKSHIRUVI
# ==============================================================================
@router.message(RegistrationFSM.waiting_phone)
async def handle_phone(message: types.Message, state: FSMContext):
    """Telegram Contact obyektini qabul qiladi va ID tengligini tekshiradi."""
    user_data = await state.get_data()
    lang = user_data.get("lang", "uz")

    # 1. Agar foydalanuvchi tugmani bosmay, matn yozib yuborgan bo'lsa:
    if not message.contact:
        # Foydalanuvchi "⬅️ Orqaga" tugmasini bosgani mumkin
        if message.text and message.text.startswith("⬅️"):
            # Ro'yxatdan o'tishni bekor qilish va asosiy menyuga qaytish
            from bot.keyboards.reply import main_menu_kb
            await state.clear()
            await message.answer(
                get_text("register.cancelled", lang),
                reply_markup=main_menu_kb(lang)
            )
            return
        await message.answer(
            get_text("register.must_use_contact_button", lang),
            reply_markup=contact_request_keyboard(lang)
        )
        return

    # 2. XAVFSIZLIK TEKSHIRUVI: Yuborilgan kontakt ushbu foydalanuvchining o'zinikimi?
    if message.contact.user_id != message.from_user.id:
        await message.answer(
            "⚠️ Bu sizning raqamingiz emas! Iltimos, pastdagi tugmani bosing.",
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
        reply_markup=cefr_level_selection(lang)  # A1, A2, B1, B2, C1, C2 tugmalari
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
            reply_markup=cefr_level_selection(lang)
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
        success = await register_user_in_db(
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            level=level,
            lang=lang
        )

        if success:
            # Ro'yxatdan o'tish muvaffaqiyatli tugadi: State tozalanadi
            await state.clear()
            
            await message.answer(
                get_text("register.success_welcome", lang),
                reply_markup=registered_menu_kb(lang)  # Ro'yxatdan o'tganlar menyusi!
            )
        else:
            await message.answer(
                get_text("error.server_error", lang),
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



import httpx
from typing import Optional
from bot.config import settings

# API URL
REGISTER_INIT_URL = f"{settings.API_BASE_URL}/api/auth/register"

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
            "level": level,
            "language": lang,
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


async def register_user_in_db(
    telegram_id: int,
    name: str,
    phone: str,
    level: str,
    lang: str = "uz"
) -> bool:
    """
    Handler tomonidan ishlatiladigan helper funksiya.
    Email/Parol telegram foydalanuvchisidan so'ralmagani sababli avtomatik generatsiya qilinadi.
    Muvaffaqiyatli o'tsa True, aks holda False qaytaradi.
    """
    # Backend email va password talab qilsa, zaxira qiymatlar yaratiladi:
    email = f"user_{telegram_id}@myestro.local"
    password = f"tg_pass_{telegram_id}"

    tokens, user_info = await _register_user(
        telegram_id=telegram_id,
        name=name,
        email=email,
        password=password,
        phone=phone,
        level=level,
        lang=lang,
    )

    # Agar tokenlar qaytgan bo'lsa ro'yxatdan o'tish muvaffaqiyatli hisoblanadi
    return tokens is not None
