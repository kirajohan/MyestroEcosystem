"""Menu handlers — reply keyboard routing + callback handlers.

Covers:
- Language selection from /start
- NOT_REGISTERED_USER_SECTION (About, Guide, Language, Admin, Register)
- REGISTERED_USER_SECTION (Profile, Settings, Guide, Admin, Video, File)
"""

from aiogram import Router, types, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from bot.states.registration import (
    StartSection, RegistrationFSM, MenuSection, RegisteredSection,
)
from bot.keyboards.reply import (
    language_selection_keyboard, main_menu_keyboard, registered_menu_keyboard,
    contact_request_keyboard, remove_keyboard,
)
from bot.config import settings, API_BASE_URL
import httpx
from bot.keyboards.inline import (
    language_selection, language_switch_kb, about_us_kb, guide_kb,
    phone_request_kb, registration_restart_kb, cefr_level_selection,
    settings_kb, registered_menu_kb, confirm_kb, admin_contact_kb,
)
from bot.utils.i18n import get_text

router = Router()


# ══════════════════════════════════════════════════════════════
# LANGUAGE SELECTION (from /start)
# ══════════════════════════════════════════════════════════════

@router.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]))
async def language_selected(message: types.Message, state: FSMContext):
    """Handle language selection from /start reply keyboard."""
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
        reply_markup=main_menu_keyboard(lang),
    )


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")


LIMIT = 5


async def fetch_content_list(content_type: str, page: int):
    """Bazadan paginatsiya bilan content olish.

    Returns: (items_list, total_count)
    """
    offset = (page - 1) * LIMIT
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/content/public?content_type={content_type}&limit={LIMIT}&offset={offset}"
            )
            if resp.status_code == 200:
                items = resp.json()
                # Umumiy sonni olish uchun alohida so'rov
                total_resp = await client.get(
                    f"{API_BASE_URL}/content/public?content_type={content_type}&limit=1000&offset=0"
                )
                total = len(total_resp.json()) if total_resp.status_code == 200 else len(items)
                return items, total
    except Exception as e:
        print(f"[CONTENT FETCH ERROR] {e}")
    return [], 0


def build_content_keyboard(items, content_type: str, page: int, total: int, lang: str):
    """Paginatsiyali InlineKeyboard yaratish."""
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()

    # Har bir item uchun tugma
    prefix = "video" if content_type == "video" else "file"
    for i, item in enumerate(items, 1):
        title = item.get("title", f"{prefix.capitalize()} #{i}")
        idx = (page - 1) * LIMIT + i
        label = f"{idx}. {title}"
        builder.button(text=label, callback_data=f"{prefix}_select_{item['id']}")

    # Navigatsiya tugmalari
    total_pages = max(1, (total + LIMIT - 1) // LIMIT)
    nav_buttons = []

    if page > 1:
        nav_buttons.append(("⬅️", f"content:{content_type}:page_{page - 1}"))

    nav_buttons.append((f"{page}/{total_pages}", "noop"))

    if page < total_pages:
        nav_buttons.append(("➡️", f"content:{content_type}:page_{page + 1}"))

    for text, cb in nav_buttons:
        builder.button(text=text, callback_data=cb)

    # Orqaga tugmasi
    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")
    builder.button(text=back_text, callback_data="back_to_menu")

    # Layout: har bir content alohida qator, navigatsiya bitta qator, back alohida
    builder.adjust(1, len(nav_buttons), 1)
    return builder.as_markup()


async def send_content_list(target, content_type: str, page: int, lang: str, edit: bool = False):
    """Content ro'yxatini yuborish yoki tahrirlash."""
    items, total = await fetch_content_list(content_type, page)

    if not items:
        text_key = "video.not_found" if content_type == "video" else "file.not_found"
        if edit and hasattr(target, 'edit_text'):
            await target.edit_text(get_text(text_key, lang))
            await target.edit_reply_markup(reply_markup=None)
        else:
            await target.answer(get_text(text_key, lang))
        return

    header = "🎬 Video darsliklar" if content_type == "video" else "📁 File darsliklar"
    text = f"<b>{header}</b>\n\nKerakli darsni tanlang:"
    keyboard = build_content_keyboard(items, content_type, page, total, lang)

    if edit and hasattr(target, 'edit_text'):
        await target.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


# ══════════════════════════════════════════════════════════════
# MAIN MENU — REPLY KEYBOARD HANDLERS (NOT_REGISTERED)
# ══════════════════════════════════════════════════════════════

# --- Register/Login is now handled by register.py router ---


# --- About Us ---
@router.message((F.text.in_([
    "ℹ️ Biz haqimizda", "ℹ️ О нас", "ℹ️ About us",
])) | Command("about"))
async def cmd_about(message: types.Message, state: FSMContext):
    """Handle About Us — show info + inline sub-menu."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.about_us)

    await message.answer(
        get_text("about.text", lang),
        reply_markup=about_us_kb(lang),
    )


# --- Guide ---
@router.message((F.text.in_([
    "📖 Qo'llanma", "📖 Руководство", "📖 Guide",
])) | Command("guide"))
async def cmd_guide(message: types.Message, state: FSMContext):
    """Handle Guide — show info + inline sub-menu."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.guide)

    await message.answer(
        get_text("guide.text", lang),
        reply_markup=guide_kb(lang),
    )


# --- Language ---
@router.message((F.text.in_([
    "🌐 Til/Language", "🌐 Язык", "🌐 Language",
])) | Command("language"))
async def cmd_language(message: types.Message, state: FSMContext):
    """Handle Language selection — show inline language picker."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)

    await message.answer(
        get_text("language.prompt", lang),
        reply_markup=language_selection(include_back=True),
    )


# --- Admin Message ---
@router.message((F.text.in_([
    "📨 Admin ga xabar", "📨 Написать админу", "📨 Message admin",
])) | Command("admin"))
async def cmd_admin_message(message: types.Message, state: FSMContext):
    """Handle Admin Message — show instructions + inline keyboard."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.contact_admin)

    await message.answer(
        get_text("admin.instruction", lang),
        reply_markup=admin_contact_kb(lang),
    )


# ══════════════════════════════════════════════════════════════
# REGISTERED USER — REPLY KEYBOARD HANDLERS (message, not callback)
# ══════════════════════════════════════════════════════════════

@router.message((F.text.in_(["👤 Profil", "👤 Профиль", "👤 Profile"])) | Command("profile"))
async def msg_profile(message: types.Message, state: FSMContext):
    """Reply keyboard → Profile."""
    from bot.handlers.profile import show_profile
    await show_profile(message, state, from_callback=False)


@router.message((F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings"])) | Command("settings"))
async def msg_settings(message: types.Message, state: FSMContext):
    """Reply keyboard → Settings."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.settings)

    await message.answer(
        get_text("settings.title", lang),
        reply_markup=settings_kb(lang),
    )


@router.message((F.text.in_(["📖 Qo'llanma", "📖 Руководство", "📖 Guide"])) | Command("guide"))
async def msg_guide(message: types.Message, state: FSMContext):
    """Reply keyboard → Guide."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await message.answer(get_text("guide.text", lang))


@router.message((F.text.in_(["📨 Admin ga xabar", "📨 Написать админу", "📨 Message admin"])) | Command("admin"))
async def msg_admin(message: types.Message, state: FSMContext):
    """Reply keyboard → Admin contact."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.contact_admin)
    await message.answer(
        get_text("admin.instruction", lang),
        reply_markup=admin_contact_kb(lang),
    )


@router.message((F.text.in_(["🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson"])) | Command("video"))
async def msg_video(message: types.Message, state: FSMContext):
    """Reply keyboard → Video lessons (paginated)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(message, "video", 1, lang, edit=False)


@router.message((F.text.in_(["📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons"])) | Command("file"))
async def msg_file(message: types.Message, state: FSMContext):
    """Reply keyboard → File lessons (paginated)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(message, "file", 1, lang, edit=False)


# ══════════════════════════════════════════════════════════════
# ABOUT US — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'back to menu' — show correct main menu based on registration state."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    registration_complete = user_data.get("registration_complete", False)

    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
        await callback.message.edit_text(get_text("main_menu", lang))
        await callback.message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_keyboard(lang),
        )
    else:
        await state.set_state(StartSection.main_menu)
        await callback.message.edit_text(get_text("main_menu", lang))
        await callback.message.answer(
            get_text("main_menu", lang),
            reply_markup=main_menu_keyboard(lang),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("about_"))
async def about_callbacks(callback: types.CallbackQuery, state: FSMContext):
    """Handle About Us sub-menu buttons."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    key_map = {
        "about_links": "about.links",
        "about_ecosystem": "about.ecosystem",
        "about_faq": "about.faq",
    }
    text_key = key_map.get(callback.data, "about.text")

    await callback.message.edit_text(
        get_text(text_key, lang),
        reply_markup=about_us_kb(lang),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# GUIDE — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("guide_"))
async def guide_callbacks(callback: types.CallbackQuery, state: FSMContext):
    """Handle Guide sub-menu buttons."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    key_map = {
        "guide_bot": "guide.bot",
        "guide_ai": "guide.ai",
        "guide_faq": "about.faq",
    }
    text_key = key_map.get(callback.data, "guide.text")

    await callback.message.edit_text(
        get_text(text_key, lang),
        reply_markup=guide_kb(lang),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# LANGUAGE — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.in_(["lang_uz", "lang_ru", "lang_en"]))
async def change_language(callback: types.CallbackQuery, state: FSMContext):
    """Handle language change from inline keyboard."""
    new_lang = callback.data.split("_")[1]
    await state.update_data(lang=new_lang)

    # Check if we're in settings or main menu
    current_state = await state.get_state()
    user_data = await state.get_data()
    registration_complete = user_data.get("registration_complete", False)

    if current_state == "MenuSection:language_selection" and not registration_complete:
        # Non-registered user changing language from main menu
        await state.set_state(StartSection.main_menu)
        await callback.message.edit_text(
            get_text("start.language_changed", new_lang),
        )
        await callback.message.answer(
            get_text("main_menu", new_lang),
            reply_markup=main_menu_keyboard(new_lang),
        )
    else:
        # Registered user (or any other case) — return to registered main menu
        await state.set_state(RegisteredSection.main_menu)
        await callback.message.edit_text(
            get_text("start.language_changed", new_lang),
        )
        await callback.message.answer(
            get_text("main_menu", new_lang),
            reply_markup=registered_menu_keyboard(new_lang),
        )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# PHONE SHARE — CALLBACK
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "phone_share")
async def phone_share_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'Raqam yuborish' button — show contact request keyboard."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await callback.message.answer(
        get_text("registration.phone_request", lang),
        reply_markup=contact_request_keyboard(),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# REGISTRATION — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "reg_restart")
async def registration_restart(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'Boshidan boshlash' — restart registration."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(RegistrationFSM.waiting_name)

    await callback.message.edit_text(get_text("registration.ask_name", lang))
    await callback.answer()


@router.callback_query(F.data == "confirm_yes")
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    """Confirm — end registration and go to registered section."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.update_data(registration_complete=True)
    await state.set_state(RegisteredSection.main_menu)

    await callback.message.edit_text(get_text("registration.done", lang))
    await callback.message.answer(
        get_text("registered.welcome_new", lang),
        reply_markup=registered_menu_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_no")
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    """Don't confirm — go back to name input."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(RegistrationFSM.waiting_name)

    await callback.message.edit_text(get_text("registration.ask_name", lang))
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# REGISTERED USER — MENU CALLBACKS
# ══════════════════════════════════════════════════════════════

# NOTE: menu_profile is handled by handlers/profile.py


@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: types.CallbackQuery, state: FSMContext):
    """Show settings menu."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.settings)

    await callback.message.edit_text(
        get_text("settings.title", lang),
        reply_markup=settings_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_guide")
async def menu_registered_guide(callback: types.CallbackQuery, state: FSMContext):
    """Show guide for registered users."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await callback.message.answer(
        get_text("guide.text", lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_admin_msg")
async def menu_registered_admin(callback: types.CallbackQuery, state: FSMContext):
    """Start admin message from registered menu."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.contact_admin)

    await callback.message.answer(
        get_text("admin.instruction", lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_video")
async def menu_video(callback: types.CallbackQuery, state: FSMContext):
    """Show video lessons from Content DB (paginated)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(callback.message, "video", 1, lang, edit=False)
    await callback.answer()


@router.callback_query(F.data == "menu_file")
async def menu_file(callback: types.CallbackQuery, state: FSMContext):
    """Show file lessons from Content DB (paginated)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(callback.message, "file", 1, lang, edit=False)
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# CONTENT PAGINATION — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("content:video:page_"))
async def content_video_page(callback: types.CallbackQuery, state: FSMContext):
    """Video darsliklar sahifasini almashtirish."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    page = int(callback.data.split("_")[-1])
    await send_content_list(callback.message, "video", page, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("content:file:page_"))
async def content_file_page(callback: types.CallbackQuery, state: FSMContext):
    """File darsliklar sahifasini almashtirish."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    page = int(callback.data.split("_")[-1])
    await send_content_list(callback.message, "file", page, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("video_select_"))
async def video_select(callback: types.CallbackQuery, state: FSMContext):
    """Send selected video to user."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    content_id = int(callback.data.split("_")[2])

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{API_BASE_URL}/content/public")
            if resp.status_code == 200:
                all_content = resp.json()
                video = next((c for c in all_content if c["id"] == content_id), None)
                if video:
                    title = video.get("title", "Video")
                    desc = video.get("description", "")
                    tg_file_id = video.get("telegram_file_id", "")

                    text = f"🎬 <b>{title}</b>\n{desc}" if desc else f"🎬 <b>{title}</b>"

                    if tg_file_id:
                        await callback.message.answer_video(video=tg_file_id, caption=text, parse_mode="HTML")
                    else:
                        await callback.message.answer(
                            text + "\n\n❌ Video hali tayyor emas (file_id yo'q)"
                        )
                else:
                    await callback.message.answer(get_text("video.not_found", lang))
            else:
                await callback.message.answer(get_text("video.not_found", lang))
    except Exception as e:
        print(f"[VIDEO SEND ERROR] {e}")
        await callback.message.answer(get_text("video.not_found", lang))

    await callback.answer()


@router.callback_query(F.data.startswith("file_select_"))
async def file_select(callback: types.CallbackQuery, state: FSMContext):
    """Send selected file to user."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    content_id = int(callback.data.split("_")[2])

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{API_BASE_URL}/content/public")
            if resp.status_code == 200:
                all_content = resp.json()
                file_item = next((c for c in all_content if c["id"] == content_id), None)
                if file_item:
                    title = file_item.get("title", "File")
                    desc = file_item.get("description", "")
                    tg_file_id = file_item.get("telegram_file_id", "")

                    text = f"📁 <b>{title}</b>\n{desc}" if desc else f"📁 <b>{title}</b>"

                    if tg_file_id:
                        await callback.message.answer_document(document=tg_file_id, caption=text, parse_mode="HTML")
                    else:
                        await callback.message.answer(
                            text + "\n\n❌ Fayl hali tayyor emas (file_id yo'q)"
                        )
                else:
                    await callback.message.answer(get_text("file.not_found", lang))
            else:
                await callback.message.answer(get_text("file.not_found", lang))
    except Exception as e:
        print(f"[FILE SEND ERROR] {e}")
        await callback.message.answer(get_text("file.not_found", lang))

    await callback.answer()


# ══════════════════════════════════════════════════════════════
# SETTINGS — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "settings_language")
async def settings_language(callback: types.CallbackQuery, state: FSMContext):
    """Show language selection from settings."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)

    await callback.message.edit_text(
        get_text("language.prompt", lang),
        reply_markup=language_switch_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: types.CallbackQuery, state: FSMContext):
    """Back to settings from language selection."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await callback.message.edit_text(
        get_text("settings.title", lang),
        reply_markup=settings_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_logout")
async def settings_logout(callback: types.CallbackQuery, state: FSMContext):
    """Handle logout — clear state and return to start."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await state.clear()
    await callback.message.answer(
        get_text("settings.logout_done", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_ai_toggle")
async def settings_ai_toggle(callback: types.CallbackQuery, state: FSMContext):
    """Toggle AI ON/OFF — sync with Backend API."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    ai_enabled = user_data.get("ai_enabled", True)
    user_id = user_data.get("telegram_id") or callback.from_user.id
    user_data_api = None

    # Toggle locally first
    new_status = not ai_enabled

    # Try to sync with Backend API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/users/{user_id}/ai-toggle",
                json={"ai_enabled": new_status},
            )
            if resp.status_code == 200:
                user_data_api = resp.json()
            else:
                # Backend failed — revert local toggle
                new_status = ai_enabled
                await callback.answer(get_text("error", lang))
                return
    except Exception:
        # Backend unreachable — revert
        new_status = ai_enabled
        await callback.answer(get_text("error", lang))
        return

    # Update local state
    await state.update_data(ai_enabled=new_status)

    # Notify user
    status_text = get_text("ai.enabled" if new_status else "ai.disabled", lang)
    await callback.answer(status_text, show_alert=True)

    # Refresh settings menu
    await callback.message.edit_text(
        get_text("settings.title", lang),
        reply_markup=settings_kb(lang),
    )


# ══════════════════════════════════════════════════════════════
# ADMIN CONTACT SESSION — SAVE TO BACKEND (not Telegram forward)
# ══════════════════════════════════════════════════════════════

@router.message(
    F.chat.type == "private",
    F.content_type.in_({"text", "photo", "voice", "document", "video", "sticker"}),
    StateFilter(MenuSection.contact_admin),
)
async def handle_admin_contact_session(message: types.Message, state: FSMContext):
    """Save user message to backend admin_messages table (inbox)."""

    user_data = await state.get_data()
    lang = _get_lang(user_data)
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "User"
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    db_user_id = user_data.get("id")

    # Determine content type and extract data
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

    # Save to backend
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
                print(f"[ADMIN SAVE ERROR] {resp.status_code}: {resp.text}")
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
