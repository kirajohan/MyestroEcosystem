from aiogram import Router, types, F
from aiogram.filters import StateFilter, Command, or_f
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import (
    language_selection, main_menu, registered_menu_kb,
    contact_request_keyboard, remove_keyboard,
    cefr_level_selection, settings_kb, guide_kb, about_us_kb,
    language_switch_kb, confirm_kb, admin_contact_kb,
    registration_restart_kb,
    content_submenu_kb,  # ⭐ YANGI
)
from bot.states.registration import (
    StartSection, RegistrationFSM, MenuSection, RegisteredSection,
    QuizSection,  # ⭐ YANGI
)

from bot.config import settings, API_BASE_URL
import httpx
from bot.utils.i18n import get_text
from bot.states.registrations_filter import IsRegistered, IsNotRegistered

router = Router()

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")

LIMIT = 5

async def fetch_content_list(content_type: str, page: int = 1):
    """Paginatsiya bilan content fetch."""
    offset = (page - 1) * LIMIT
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/content/public?content_type={content_type}&limit={LIMIT}&offset={offset}"
            )
            if resp.status_code == 200:
                items = resp.json()
                total_resp = await client.get(
                    f"{API_BASE_URL}/content/public?content_type={content_type}&limit=1000&offset=0"
                )
                total = len(total_resp.json()) if total_resp.status_code == 200 else len(items)
                return items, total
    except Exception as e:
        print(f"[CONTENT FETCH ERROR] {e}")
    return [], 0


# ══════════════════════════════════════════════════════════════
# LANGUAGE SELECTION (from /start) — ONLY UNREGISTERED
# ══════════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]),
    StateFilter(StartSection.main_menu),  # <-- BU QO'SHILDI
)
async def language_selected(message: types.Message, state: FSMContext):
    """Language selection — reply keyboard button (FIRST TIME ONLY)."""
    lang_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
    }
    lang = lang_map.get(message.text, "uz")
    await state.update_data(lang=lang)
    await state.set_state(StartSection.main_menu)

    await message.answer(
        get_text("start.language_changed", lang),
        reply_markup=main_menu(lang),
    )


# ══════════════════════════════════════════════════════════════
# LANGUAGE CHANGE (from Settings) — REGISTERED OR UNREGISTERED
# ══════════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]),
    StateFilter(MenuSection.language_selection),  # <-- BU QO'SHILDI
)
async def change_language_reply(message: types.Message, state: FSMContext):
    """Language switch dari menu."""
    lang_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
    }
    new_lang = lang_map.get(message.text, "uz")
    await state.update_data(lang=new_lang)

    user_data = await state.get_data()
    registration_complete = user_data.get("registration_complete", False)

    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
        await message.answer(
            get_text("start.language_changed", new_lang),
            reply_markup=registered_menu_kb(new_lang),
        )
    else:
        await state.set_state(StartSection.main_menu)
        await message.answer(
            get_text("start.language_changed", new_lang),
            reply_markup=main_menu(new_lang),
        )

# ══════════════════════════════════════════════════════════════
# MAIN MENU — ABOUT US (NOT_REGISTERED)
# ══════════════════════════════════════════════════════════════

@router.message(or_f(
    F.text.in_(["ℹ️ Biz haqimizda", "ℹ️ О нас", "ℹ️ About us"]),
    Command("about"),
))
async def cmd_about(message: types.Message, state: FSMContext):
    """About Us — submenu."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.about_us)

    await message.answer(
        get_text("about.text", lang),
        reply_markup=about_us_kb(lang),
    )


# ═══ ABOUT US — SUBMENU ═════════════════════════════════════

@router.message(F.text.in_(["🔗 Havolalar", "🔗 Ссылки", "🔗 Links"]))
async def about_links(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("about.links", lang),
        reply_markup=about_us_kb(lang),
    )

@router.message(F.text.in_(["🌐 Ecosystem Haqida", "🌐 Об экосистеме", "🌐 About Ecosystem"]))
async def about_ecosystem(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("about.ecosystem", lang),
        reply_markup=about_us_kb(lang),
    )

@router.message(F.text.in_(["❓ FAQ", "❓ ЧаВО", "❓ FAQ"]))
async def about_faq(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("about.faq", lang),
        reply_markup=about_us_kb(lang),
    )


# ══════════════════════════════════════════════════════════════
# MAIN MENU — GUIDE (NOT_REGISTERED)
# ══════════════════════════════════════════════════════════════

@router.message(or_f(
    F.text.in_(["📖 Qo'llanma", "📖 Руководство", "📖 Guide"]),
    Command("guide"),
))
async def cmd_guide(message: types.Message, state: FSMContext):
    """Guide menu."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.guide)

    await message.answer(
        get_text("guide.text", lang),
        reply_markup=guide_kb(lang),
    )


# ═══ GUIDE — SUBMENU ════════════════════════════════════════

@router.message(F.text.in_(["🤖 Bot bo'yicha", "🤖 О боте", "🤖 About Bot"]))
async def guide_bot(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("guide.bot", lang),
        reply_markup=guide_kb(lang),
    )

@router.message(F.text.in_(["🧠 AI bo'yicha", "🧠 Об AI", "🧠 About AI"]))
async def guide_ai(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("guide.ai", lang),
        reply_markup=guide_kb(lang),
    )


# ══════════════════════════════════════════════════════════════
# MAIN MENU — LANGUAGE
# ══════════════════════════════════════════════════════════════

@router.message(F.text.in_(["🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]))
async def settings_language_reply(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)  # <-- State o'zgaradi

    await message.answer(
        get_text("language.prompt", lang),
        reply_markup=language_switch_kb(lang),
    )


@router.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]))
async def change_language_reply(message: types.Message, state: FSMContext):
    """Language switch dari menu."""
    lang_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru",
        "🇬🇧 English": "en",
    }
    new_lang = lang_map.get(message.text, "uz")
    await state.update_data(lang=new_lang)

    user_data = await state.get_data()
    registration_complete = user_data.get("registration_complete", False)

    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
    else:
        await state.set_state(StartSection.main_menu)

    await message.answer(
        get_text("start.language_changed", new_lang),
        reply_markup=registered_menu_kb(new_lang) if registration_complete else main_menu(new_lang),
    )


# ══════════════════════════════════════════════════════════════
# MAIN MENU — ADMIN MESSAGE (NOT_REGISTERED)
# ══════════════════════════════════════════════════════════════

@router.message(or_f(
    F.text.in_(["📨 Admin ga xabar", "📨 Написать админу", "📨 Message admin"]),
    Command("admin"),
))
async def cmd_admin_message(message: types.Message, state: FSMContext):
    """Start admin contact session."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.contact_admin)

    await message.answer(
        get_text("admin.instruction", lang),
        reply_markup=admin_contact_kb(lang),
    )


# ════════════════════════════════════════════════════════════
# BACK TO MAIN MENU (UNIVERSAL)
# ════════════════════════════════════════════════════════════

@router.message(F.text.in_(["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "⬅️ Orqaga qaytish"]))
async def back_to_main_menu_reply(message: types.Message, state: FSMContext):
    """Back to main menu — universal handler."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    registration_complete = user_data.get("registration_complete", False)

    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang),
        )
    else:
        await state.set_state(StartSection.main_menu)
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=main_menu(lang),
        )


# ══════════════════════════════════════════════════════════════
# REGISTERED USER — MENU ITEMS
# ══════════════════════════════════════════════════════════════

from bot.states.registration import IsRegisteredFilter

# Registered user commandalari uchun:
@router.message(
    IsRegistered(),
    or_f(
        F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings"]),
        Command("settings"),
    ),
)
async def msg_settings(message: types.Message, state: FSMContext):
    """Settings menu — ONLY REGISTERED."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.settings)

    await message.answer(
        get_text("settings.title", lang),
        reply_markup=settings_kb(lang),
    )


@router.message(
    IsRegistered(),
    or_f(
        F.text.in_(["👤 Profil", "👤 Профиль", "👤 Profile"]),
        Command("profile"),
    ),
)
async def msg_profile(message: types.Message, state: FSMContext):
    """User profile — ONLY REGISTERED."""
    from bot.handlers.profile import show_profile
    await show_profile(message, state, from_callback=False)


# Unregistered user uchun:
@router.message(
    Command("register"),
    IsRegisteredFilter(is_registered=False),
)
async def msg_register(message: types.Message, state: FSMContext):
    """Register - ONLY for unregistered users."""
    from bot.handlers.register import start_registration
    await start_registration(message, state)



# ══════════════════════════════════════════════════════════════
# REGISTERED USER — TEST'S (English QUIZ)
# ══════════════════════════════════════════════════════════════

@router.message(
    IsRegistered(),
    F.text.in_(["🧪 Test's (English QUIZ)", "🧪 Тесты (English QUIZ)"]),
)
async def msg_quiz_start(message: types.Message, state: FSMContext):
    """🧪 Test's bosilganda — CEFR daraja tanlash."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await state.set_state(QuizSection.cefr_selection)

    await message.answer(
        get_text("quiz.select_cefr", lang),  # "Qaysi darajada test?"
        reply_markup=cefr_level_selection(),  # ✅ allaqachon bor keyboard
    )


@router.message(
    QuizSection.cefr_selection,
    F.text.in_(["A0", "A1", "A2", "B1", "B2", "C1", "C2"]),
)
async def msg_quiz_cefr_selected(message: types.Message, state: FSMContext):
    """CEFR daraja tanlandi — testlar ro'yxati (inline keyboard)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    cefr_level = message.text

    await state.update_data(quiz_cefr=cefr_level)
    await state.set_state(QuizSection.quiz_list)

    # Keyingi qadamda: Backend API dan testlarni olib, inline keyboard chiqaramiz
    await message.answer(
        f"📊 <b>{cefr_level}</b> darajasidagi testlar yuklanmoqda...",
        parse_mode="HTML",
    )
    # TODO: fetch_quiz_list(cefr_level) chaqirib, inline pagination keyboard chiqarish



# ═══ SETTINGS — SUBMENU ═════════════════════════════════════

@router.message(F.text.in_(["🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]))
async def settings_language_reply(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)

    await message.answer(
        get_text("language.prompt", lang),
        reply_markup=language_switch_kb(lang),
    )

@router.message(F.text.in_(["🤖 AI ON/OFF", "🤖 AI ВКЛ/ВЫКЛ", "🤖 AI Yoqish/O'chirish"]))
async def settings_ai_toggle_reply(message: types.Message, state: FSMContext):
    """Toggle AI ON/OFF."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    ai_enabled = user_data.get("ai_enabled", True)
    
    # DEBUG: State ma'lumotlarini ko'rsatish
    print(f"[AI TOGGLE] Current state data: {user_data}")
    print(f"[AI TOGGLE] Current ai_enabled: {ai_enabled}")
    
    # Database user ID ni olish
    db_user_id = user_data.get("id")
    telegram_id = message.from_user.id
    
    if not db_user_id:
        await message.answer(
            get_text("error.user_not_found", lang),
            reply_markup=settings_kb(lang),
        )
        return

    # Toggle status
    new_status = not ai_enabled
    print(f"[AI TOGGLE] Toggling from {ai_enabled} to {new_status}")

    # Sync with Backend
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # API endpoint ni tekshiring
            endpoint = f"{API_BASE_URL}/sync/users/{db_user_id}/ai-toggle"
            print(f"[AI TOGGLE] Calling endpoint: {endpoint}")
            
            resp = await client.put(
                endpoint,
                json={"ai_enabled": new_status},
            )
            
            print(f"[AI TOGGLE] Response status: {resp.status_code}")
            print(f"[AI TOGGLE] Response body: {resp.text}")
            
            if resp.status_code != 200:
                new_status = ai_enabled  # Revert
                await message.answer(
                    get_text("error.sync", lang),
                    reply_markup=settings_kb(lang),
                )
                return
    except Exception as e:
        print(f"[AI TOGGLE ERROR] {e}")
        new_status = ai_enabled
        await message.answer(
            get_text("error.sync", lang),
            reply_markup=settings_kb(lang),
        )
        return

    # Update state
    await state.update_data(ai_enabled=new_status)
    print(f"[AI TOGGLE] State updated: ai_enabled={new_status}")

    # Notify
    status_text = get_text("ai.enabled" if new_status else "ai.disabled", lang)
    await message.answer(
        f"✅ {status_text}",
        reply_markup=settings_kb(lang),
    )

@router.message(F.text.in_(["🚪 Log Out", "🚪 Выйти", "🚪 Chiqish"]))
async def settings_logout_reply(message: types.Message, state: FSMContext):
    """Logout — clear state."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await state.clear()
    await message.answer(
        get_text("settings.logout_done", lang),
        reply_markup=main_menu(lang),
    )


# ══════════════════════════════════════════════════════════════
# REGISTERED USER — CONTENT SUBMENU (📚 Darsliklar)
# ══════════════════════════════════════════════════════════════

@router.message(
    IsRegistered(),
    F.text.in_(["📚 Darsliklar", "📚 Учебные материалы", "📚 Lessons"]),
)
async def msg_content_submenu(message: types.Message, state: FSMContext):
    """📚 Darsliklar bosilganda — submenu chiqadi (Video + File)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await message.answer(
        get_text("content.select_type", lang),  # "Qaysi turdagi darslik?"
        reply_markup=content_submenu_kb(lang),
    )



@router.message(
    IsRegistered(),
    or_f(
        F.text.in_(["🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson"]),
        Command("video"),
    ),
)
async def msg_video(message: types.Message, state: FSMContext):
    """Video lessons list."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    items, total = await fetch_content_list("video", 1)

    if not items:
        await message.answer(get_text("video.not_found", lang))
        return

    # ✅ escape_html YO'Q — oddiy text
    lines = [f"{i+1}. {item['title']}" for i, item in enumerate(items)]
    text = "🎬 <b>Video Darsliklar</b>\n\n" + "\n".join(lines) + f"\n\n(Jami: {total} ta)"

    await message.answer(text, parse_mode="HTML")

    pass

@router.message(
    IsRegistered(),
    or_f(
        F.text.in_(["📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons"]),
        Command("file"),
    ),
)
async def msg_file(message: types.Message, state: FSMContext):
    """File lessons list."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    items, total = await fetch_content_list("file", 1)

    if not items:
        await message.answer(get_text("file.not_found", lang))
        return

    # ✅ escape_html YO'Q — oddiy text
    lines = [f"{i+1}. {item['title']}" for i, item in enumerate(items)]
    text = "📁 <b>File Darsliklar</b>\n\n" + "\n".join(lines) + f"\n\n(Jami: {total} ta)"

    await message.answer(text, parse_mode="HTML")

    pass
# ══════════════════════════════════════════════════════════════
# REGISTRATION — CONFIRMATION
# ══════════════════════════════════════════════════════════════

@router.message(F.text.in_(["✅ Ha", "✅ Да", "✅ Yes"]))
async def confirm_yes_reply(message: types.Message, state: FSMContext):
    """Confirm registration — YES."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    current_state = await state.get_state()
    
    if current_state == "RegistrationFSM:waiting_confirmation":
        await state.update_data(registration_complete=True)
        await state.set_state(RegisteredSection.main_menu)

        await message.answer(
            get_text("registration.done", lang),
        )
        await message.answer(
            get_text("registered.welcome_new", lang),
            reply_markup=registered_menu_kb(lang),
        )


@router.message(F.text.in_(["❌ Yo'q", "❌ Нет", "❌ No"]))
async def confirm_no_reply(message: types.Message, state: FSMContext):
    """Confirm registration — NO."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    current_state = await state.get_state()
    
    if current_state == "RegistrationFSM:waiting_confirmation":
        await state.set_state(RegistrationFSM.waiting_name)
        await message.answer(get_text("registration.ask_name", lang))


# ══════════════════════════════════════════════════════════════
# REGISTRATION — PHONE SHARE
# ══════════════════════════════════════════════════════════════

@router.message(F.contact)
async def phone_contact_handler(message: types.Message, state: FSMContext):
    """Handle contact sharing."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"
    
    await state.update_data(phone=phone)
    await message.answer(
        get_text("registration.phone_confirmed", lang),
        reply_markup=remove_keyboard,
    )


# ══════════════════════════════════════════════════════════════
# ADMIN CONTACT SESSION — TEXT MESSAGES
# ══════════════════════════════════════════════════════════════

@router.message(
    F.chat.type == "private",
    StateFilter(MenuSection.contact_admin),
)
async def handle_admin_contact_text(message: types.Message, state: FSMContext):
    """Save user message to admin inbox."""
    
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "User"
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    db_user_id = user_data.get("id")

    content_type = message.content_type
    text = message.text or message.caption or ""
    file_id = None

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.sticker:
        file_id = message.sticker.file_id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "user_id": db_user_id,
                "user_telegram_id": user_id,
                "user_name": f"{user_name} {username}".strip(),
                "content_type": content_type,
                "text": text,
                "file_id": file_id,
            }
            resp = await client.post(f"{API_BASE_URL}/admin-messages", json=payload)
            if resp.status_code in (200, 201):
                await message.answer(
                    get_text("admin.sent_inbox", lang),
                    reply_markup=admin_contact_kb(lang),
                )
            else:
                await message.answer(
                    get_text("admin.sent", lang),
                    reply_markup=admin_contact_kb(lang),
                )
    except Exception as e:
        print(f"[ADMIN SAVE ERROR] {e}")
        await message.answer(
            get_text("admin.sent", lang),
            reply_markup=admin_contact_kb(lang),
        )

    # ══════════════════════════════════════════════════════════════
# 🚫 FALLBACK BLOCKERS (ENG OXIRIDA BO'LISHI SHART!)
# ══════════════════════════════════════════════════════════════

@router.message(Command("settings"))
async def settings_blocked(message: types.Message, state: FSMContext):
    """Unregistered user /settings qilganda."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("error.register_first", lang),
        reply_markup=main_menu(lang),
    )


@router.message(Command("profile"))
async def profile_blocked(message: types.Message, state: FSMContext):
    """Unregistered user /profile qilganda."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("error.register_first", lang),
        reply_markup=main_menu(lang),
    )


@router.message(Command("video"))
async def video_blocked(message: types.Message, state: FSMContext):
    """Unregistered user /video qilganda."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("error.register_first", lang),
        reply_markup=main_menu(lang),
    )


@router.message(Command("file"))
async def file_blocked(message: types.Message, state: FSMContext):
    """Unregistered user /file qilganda."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("error.register_first", lang),
        reply_markup=main_menu(lang),
    )
    
# Test's — unregistered user uchun blok (mavjud pattern bo'yicha)
@router.message(Command("quiz"))
async def quiz_blocked(message: types.Message, state: FSMContext):
    """Unregistered user /quiz qilganda."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("error.register_first", lang),
        reply_markup=main_menu(lang),
    )

@router.message(Command("register"))
async def register_blocked(message: types.Message, state: FSMContext):
    """Registered user /register qilganda."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(
        get_text("error.already_registered", lang),
        reply_markup=registered_menu_kb(lang),
    )