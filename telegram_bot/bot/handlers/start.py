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



# ══════════════════════════════════════════════════════════════
# HELP COMMAND — Barcha buyruqlar ro'yxati
# ══════════════════════════════════════════════════════════════

# Buyruqlar bazasi (Yagona manba). 
# Yangi command qo'shsangiz, shu yerga qo'shasiz va /help avtomatik yangilanadi.
BOT_COMMANDS = {
    "uz": [
        ("/start", "🚀 Botni qayta ishga tushirish"),
        ("/help", "❓ Yordam va buyruqlar ro'yxati"),
        ("/about", "ℹ️ Loyiha haqida ma'lumot"),
        ("/guide", "📖 Botdan foydalanish qo'llanmasi"),
        ("/admin", "📨 Administratorga xabar yuborish"),
        ("/settings", "⚙️ Sozlamalar (ro'yxatdan o'tganlar uchun)"),
        ("/profile", "👤 Shaxsiy profilim"),
        ("/video", "🎬 Video darsliklar"),
        ("/file", "📁 Fayl darsliklar"),
    ],
    "ru": [
        ("/start", "🚀 Перезапустить бота"),
        ("/help", "❓ Список команд и помощь"),
        ("/about", "ℹ️ Информация о проекте"),
        ("/guide", "📖 Руководство по использованию"),
        ("/admin", "📨 Написать администратору"),
        ("/settings", "⚙️ Настройки (для зарегистрированных)"),
        ("/profile", "👤 Мой профиль"),
        ("/video", "🎬 Видеоуроки"),
        ("/file", "📁 Файлы уроков"),
    ],
    "en": [
        ("/start", "🚀 Restart the bot"),
        ("/help", "❓ Help and commands list"),
        ("/about", "ℹ️ About the project"),
        ("/guide", "📖 User guide"),
        ("/admin", "📨 Message the administrator"),
        ("/settings", "⚙️ Settings (for registered users)"),
        ("/profile", "👤 My profile"),
        ("/video", "🎬 Video lessons"),
        ("/file", "📁 File lessons"),
    ]
}

@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    """Yordam va barcha mavjud buyruqlar ro'yxatini chiqaradi."""
    
    def _get_lang(state_data: dict) -> str:
        return state_data.get("lang", "uz")

    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    # Tanlangan til uchun buyruqlarni olish (default: uz)
    commands_list = BOT_COMMANDS.get(lang, BOT_COMMANDS["uz"])
    
    # Chiroyli formatlash
    help_text = "📌 <b>Mavjud buyruqlar ro'yxati:</b>\n\n"
    for cmd, description in commands_list:
        help_text += f"🔹 /<b>{cmd}</b> — {description}\n"
        
    help_text += "\n💡 <i>Batafsil ma'lumot uchun /guide buyrug'idan foydalaning.</i>"
    
    await message.answer(help_text, parse_mode="HTML")