"""Start handler — /start command → DB check → keyboard select."""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from bot.keyboards.reply import (
    main_menu,
    registered_menu_kb,
    language_selection,   # ← YANGI QO'SHILDI
)
from bot.utils.i18n import get_text

router = Router()


@router.message(Command("start"))
async def start_handler(
    message: types.Message,
    state: FSMContext,
    session: AsyncSession  # ← Dependency injection
):
    """
    /start command handler.

    Flow:
    1. Clear FSM state
    2. Check database:
       - If registered: show registered_menu_kb
       - If unregistered: show main_menu_keyboard + welcome
    """

    # ✅ STEP 1: Clear FSM state
    await state.clear()

    # ✅ STEP 2: Get user Telegram ID
    user_tg_id = message.from_user.id

    # ✅ STEP 3: Check database
    stmt = select(User).where(
        (User.telegram_id == user_tg_id) &
        (User.is_active == True)  # Only active users
    )
    db_user = await session.execute(stmt)
    db_user = db_user.scalar_one_or_none()

    # ✅ STEP 4: Determine response
    if db_user:
        # ✅ REGISTERED USER
        user_lang = db_user.lang or "uz"

        # ✅ MUHIM: Registered user uchun FSM state va ma'lumotlarni saqlaymiz.
        # Bu keyinchalik register/back handlerlarda userni to'g'ri tanish uchun kerak.
        #
        # Eslatma: Import qo'shmaslik uchun state nomlari string orqali berildi.
        # Agar bot/states/registration.py ichida state nomlari boshqacha bo'lsa,
        # shu stringlarni o'sha nomlarga moslab qo'ying.
        await state.set_state("RegisteredSection:main_menu")

        await state.update_data(
            registration_complete=True,
            started_from="registered",
            user_id=db_user.id,
            telegram_id=db_user.telegram_id,
            full_name=db_user.full_name or "",
            phone=getattr(db_user, "phone", None),
            cefr_level=getattr(db_user, "cefr_level", None),
            lang=user_lang,
        )

        # Get welcome text
        welcome_key = f"menu.registered.welcome"
        welcome_text = get_text(welcome_key, user_lang)

        # Format with username/first_name
        try:
            display_name = db_user.full_name.split()[0] or message.from_user.first_name
        except:
            display_name = message.from_user.first_name

        welcome_text = welcome_text.format(name=display_name)

        # Get registered menu keyboard
        keyboard = registered_menu_kb(lang=user_lang)

        # Send response without MarkdownV2 to avoid parsing errors
        await message.answer(
            welcome_text,
            reply_markup=keyboard
        )
    else:
        # ❌ UNREGISTERED USER

        # ✅ MUHIM: Til tanlash uchun FSM state (main_menu emas, waiting_language)
        await state.set_state("StartSection:waiting_language")   # ← O'ZGARDI

        await state.update_data(
            registration_complete=False,
            started_from="unregistered",
            lang="uz",
        )

        welcome_text = (
            "👋 <b>Assalomu alaykum! Myestro AI yordamchiga xush kelibsiz!</b>\n\n"
            "Myestro — bu ingliz tilini o'rganish uchun AI-powered bepul platforma.\n"
            "AI Teacher bilan suhbatlashing, imtihon topshiring va bilimingizni oshiring!\n\n"
            "🇺🇿 Iltimos, tilni tanlang:\n"
            "🇷🇺 Пожалуйста, выберите язык:\n"
            "🇬🇧 Please choose a language:"
        )

        # ✅ TIL TANLASH KLAVIATURASI (main_menu o'rniga)
        keyboard = language_selection()   # ← O'ZGARDI

        # Send response for unregistered user
        await message.answer(
            welcome_text,
            reply_markup=keyboard
        )