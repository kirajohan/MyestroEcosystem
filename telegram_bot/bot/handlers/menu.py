"""Menu handlers — reply keyboard routing + callback handlers.

Covers:
- Language selection from /start
- NOT_REGISTERED_USER_SECTION (About, Guide, Language, Admin, Register)
- REGISTERED_USER_SECTION (Profile, Settings, Guide, Admin, Video, File)
"""

from aiogram import Router, types, F
from aiogram.filters import StateFilter, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.states.registration import (
    StartSection, RegistrationFSM, MenuSection, RegisteredSection,
)
from bot.keyboards.orange_keyboard import ColoredKeyboard
from bot.keyboards.inline import (
    language_selection, language_switch_kb, about_us_kb,
    settings_kb, admin_contact_kb,
)
from bot.config import settings, API_BASE_URL
from bot.utils.i18n import get_text
import httpx

router = Router()

# Menyudagi barcha tugmalar ro'yxati (Admin session'dan chiqish uchun)
MENU_BUTTONS = [
    "🌐 Til/Language", "🌐 Язык", "🌐 Language",
    "📝 Admin ga xabar", "📝 Написать админу", "📝 Message admin",
    "👤 Profil", "👤 Профиль", "👤 Profile",
    "⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings",
    "🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language",
    "🤖 AI ON/OFF",
    "🚪 Log Out", "🚪 Выйти",
    "🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson",
    "📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons",
    "⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "/cancel", "/start"
]


# ══════════════════════════════════════════════════════════════
# LANGUAGE SELECTION (from /start)
# ══════════════════════════════════════════════════════════════

@router.message(F.text.in_(["🇺🇿 O'zbek", "🇷🇺 Русский", "🇬🇧 English"]), StateFilter("*"))
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
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),  # 🟠 Orange tema
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

    prefix = "video" if content_type == "video" else "file"
    for i, item in enumerate(items, 1):
        title = item.get("title", f"{prefix.capitalize()} #{i}")
        idx = (page - 1) * LIMIT + i
        label = f"🟠 {idx}. {title}"
        builder.button(text=label, callback_data=f"{prefix}_select_{item['id']}")

    total_pages = max(1, (total + LIMIT - 1) // LIMIT)
    nav_buttons = []

    if page > 1:
        nav_buttons.append(("⬅️", f"content:{content_type}:page_{page - 1}"))

    nav_buttons.append((f"{page}/{total_pages}", "noop"))

    if page < total_pages:
        nav_buttons.append(("➡️", f"content:{content_type}:page_{page + 1}"))

    for text, cb in nav_buttons:
        builder.button(text=text, callback_data=cb)

    back_text = "⬅️ Orqaga" if lang == "uz" else ("⬅️ Назад" if lang == "ru" else "⬅️ Back")
    builder.button(text=back_text, callback_data="back_to_menu")

    builder.adjust(1, len(nav_buttons), 1)
    return builder.as_markup()


async def send_content_list(target, content_type: str, page: int, lang: str, edit: bool = False):
    """Content ro'yxatini yuborish yoki tahrirlash."""
    items, total = await fetch_content_list(content_type, page)

    if not items:
        text_key = "video.not_found" if content_type == "video" else "file.not_found"
        if edit and hasattr(target, 'edit_text'):
            try:
                await target.edit_text(get_text(text_key, lang))
                await target.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                pass
        else:
            await target.answer(get_text(text_key, lang))
        return

    header = "🎬 Video darsliklar" if content_type == "video" else "📁 File darsliklar"
    text = f"<b>🟠 {header}</b>\n\nKerakli darsni tanlang:"
    keyboard = build_content_keyboard(items, content_type, page, total, lang)

    if edit and hasattr(target, 'edit_text'):
        try:
            await target.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        except TelegramBadRequest:
            pass
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


# ══════════════════════════════════════════════════════════════
# SETTINGS HELPERS (shared by message handlers and callback handlers)
# ══════════════════════════════════════════════════════════════

async def _toggle_ai_core(state: FSMContext, lang: str, fallback_user_id: int = None):
    """Toggle AI enabled status in backend and FSM state.

    Returns: (success: bool, status_text: str)
    """
    user_data = await state.get_data()
    ai_enabled = user_data.get("ai_enabled", True)
    user_id = user_data.get("telegram_id") or fallback_user_id

    new_status = not ai_enabled

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.put(
                f"{API_BASE_URL}/sync/users/{user_id}/ai-toggle",
                json={"ai_enabled": new_status},
            )
            if resp.status_code != 200:
                return False, get_text("error", lang)
    except Exception:
        return False, get_text("error", lang)

    await state.update_data(ai_enabled=new_status)
    status_text = get_text("ai.enabled" if new_status else "ai.disabled", lang)
    return True, status_text


async def _do_logout(message, state: FSMContext, lang: str):
    """Logout — clear state and return to main menu with reply keyboard."""
    await state.clear()
    await state.set_state(StartSection.main_menu)
    await state.update_data(lang=lang)
    await message.answer(
        get_text("settings.logout_done", lang),
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
    )


# ══════════════════════════════════════════════════════════════
# MAIN MENU — REPLY KEYBOARD HANDLERS (StateFilter("*") bilan)
# ══════════════════════════════════════════════════════════════

@router.message(
    or_f(
        F.text.in_(["ℹ️ Biz haqimizda", "ℹ️ О нас", "ℹ️ About us"]),
        Command("about"),
    ),
    StateFilter("*")
)
async def cmd_about(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.about_us)

    await message.answer(
        get_text("about.text", lang),
        reply_markup=about_us_kb(lang),
    )


@router.message(
    or_f(
        F.text.in_(["🌐 Til/Language", "🌐 Язык", "🌐 Language"]),
        Command("language"),
    ),
    StateFilter("*")
)
async def cmd_language(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)

    await message.answer(
        get_text("language.prompt", lang),
        reply_markup=language_selection(include_back=True),
    )


@router.message(
    or_f(
        F.text.in_(["📝 Admin ga xabar", "📝 Написать админу", "📝 Message admin"]),
        Command("admin"),
    ),
    StateFilter("*")
)
async def cmd_admin_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.contact_admin)

    await message.answer(
        get_text("admin.instruction", lang),
        reply_markup=ColoredKeyboard.reply_admin_massage(lang=lang),
    )


@router.message(
    or_f(
        F.text.in_(["👤 Profil", "👤 Профиль", "👤 Profile"]),
        Command("profile"),
    ),
    StateFilter("*")
)
async def msg_profile(message: types.Message, state: FSMContext):
    from bot.handlers.profile import show_profile
    await show_profile(message, state, from_callback=False)


@router.message(
    or_f(
        F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки", "⚙️ Settings"]),
        Command("settings"),
    ),
    StateFilter("*")
)
async def msg_settings(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.settings)

    await message.answer(
        get_text("settings.title", lang),
        reply_markup=ColoredKeyboard.reply_settings_menu(lang=lang),
    )


# ══════════════════════════════════════════════════════════════
# SETTINGS SUB-MENU — REPLY KEYBOARD HANDLERS
# ══════════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["🌐 Til o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]),
    StateFilter(MenuSection.settings),
)
async def msg_settings_language(message: types.Message, state: FSMContext):
    """Settings → Language change (reply keyboard button)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)

    await message.answer(
        get_text("language.prompt", lang),
        reply_markup=language_switch_kb(lang),
    )


@router.message(
    F.text == "🤖 AI ON/OFF",
    StateFilter(MenuSection.settings),
)
async def msg_settings_ai_toggle(message: types.Message, state: FSMContext):
    """Settings → AI toggle (reply keyboard button)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    success, status_text = await _toggle_ai_core(state, lang, fallback_user_id=message.from_user.id)
    await message.answer(
        f"{status_text}\n\n{get_text('settings.title', lang)}",
        reply_markup=ColoredKeyboard.reply_settings_menu(lang=lang),
    )


@router.message(
    F.text.in_(["🚪 Log Out", "🚪 Выйти"]),
    StateFilter(MenuSection.settings),
)
async def msg_settings_logout(message: types.Message, state: FSMContext):
    """Settings → Logout (reply keyboard button)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await _do_logout(message, state, lang)


@router.message(
    F.text.in_(["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"]),
    StateFilter(MenuSection.settings),
)
async def msg_settings_back(message: types.Message, state: FSMContext):
    """Settings → Back to main menu (reply keyboard button)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    registration_complete = user_data.get("registration_complete", False)

    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
    else:
        await state.set_state(StartSection.main_menu)

    await message.answer(
        get_text("main_menu", lang),
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
    )


@router.message(
    or_f(
        F.text.in_(["🎬 Video Darslik", "🎬 Видеоурок", "🎬 Video Lesson"]),
        Command("video"),
    ),
    StateFilter("*")
)
async def msg_video(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(message, "video", 1, lang, edit=False)


@router.message(
    or_f(
        F.text.in_(["📁 File Darsliklar", "📁 Файлы уроков", "📁 File Lessons"]),
        Command("file"),
    ),
    StateFilter("*")
)
async def msg_file(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(message, "file", 1, lang, edit=False)


# ══════════════════════════════════════════════════════════════
# BACK TO MENU — FIX FOR REPLY KEYBOARD & INLINE CONFLICT
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Context-aware navigation. Fixes Inline vs Reply keyboard conflict."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    registration_complete = user_data.get("registration_complete", False)

    if registration_complete:
        await state.set_state(RegisteredSection.main_menu)
    else:
        await state.set_state(StartSection.main_menu)

    # Inline xabarni tozalaymiz
    try:
        await callback.message.delete()
    except Exception:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    # Reply Keyboard'ni yangi xabar sifatida yuboramiz (ColoredKeyboard)
    await callback.message.answer(
        get_text("main_menu", lang),
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# LANGUAGE — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.in_(["lang_uz", "lang_ru", "lang_en"]))
async def change_language(callback: types.CallbackQuery, state: FSMContext):
    new_lang = callback.data.split("_")[1]
    await state.update_data(lang=new_lang)

    current_state = await state.get_state()
    user_data = await state.get_data()
    registration_complete = user_data.get("registration_complete", False)

    target_section = StartSection.main_menu if (current_state == "MenuSection:language_selection" and not registration_complete) else RegisteredSection.main_menu
    await state.set_state(target_section)

    try:
        await callback.message.edit_text(get_text("start.language_changed", new_lang))
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        get_text("main_menu", new_lang),
        reply_markup=ColoredKeyboard.reply_main_menu(lang=new_lang),
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# PHONE SHARE & REGISTRATION — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "phone_share")
async def phone_share_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await callback.message.answer(
        get_text("registration.phone_request", lang),
        reply_markup=ColoredKeyboard.reply_contact(lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "reg_restart")
async def registration_restart(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(RegistrationFSM.waiting_name)

    try:
        await callback.message.edit_text(get_text("registration.ask_name", lang))
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(F.data == "confirm_yes")
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.update_data(registration_complete=True)
    await state.set_state(RegisteredSection.main_menu)

    try:
        await callback.message.edit_text(get_text("registration.done", lang))
    except TelegramBadRequest:
        pass

    await callback.message.answer(
        get_text("registered.welcome_new", lang),
        reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_no")
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(RegistrationFSM.waiting_name)

    try:
        await callback.message.edit_text(get_text("registration.ask_name", lang))
    except TelegramBadRequest:
        pass
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# REGISTERED USER — MENU CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.settings)

    # Delete inline message, send new message with reply keyboard
    try:
        await callback.message.delete()
    except Exception:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    await callback.message.answer(
        get_text("settings.title", lang),
        reply_markup=ColoredKeyboard.reply_settings_menu(lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_admin_msg")
async def menu_registered_admin(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.contact_admin)

    # Delete inline message if any
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        get_text("admin.instruction", lang),
        reply_markup=ColoredKeyboard.reply_admin_massage(lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_video")
async def menu_video(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(callback.message, "video", 1, lang, edit=False)
    await callback.answer()


@router.callback_query(F.data == "menu_file")
async def menu_file(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await send_content_list(callback.message, "file", 1, lang, edit=False)
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# CONTENT PAGINATION — CALLBACKS
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("content:video:page_"))
async def content_video_page(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    page = int(callback.data.split("_")[-1])
    await send_content_list(callback.message, "video", page, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("content:file:page_"))
async def content_file_page(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    page = int(callback.data.split("_")[-1])
    await send_content_list(callback.message, "file", page, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("video_select_"))
async def video_select(callback: types.CallbackQuery, state: FSMContext):
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
                        await callback.message.answer(text + "\n\n❌ Video hali tayyor emas (file_id yo'q)")
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
                        await callback.message.answer(text + "\n\n❌ Fayl hali tayyor emas (file_id yo'q)")
                else:
                    await callback.message.answer(get_text("file.not_found", lang))
            else:
                await callback.message.answer(get_text("file.not_found", lang))
    except Exception as e:
        print(f"[FILE SEND ERROR] {e}")
        await callback.message.answer(get_text("file.not_found", lang))

    await callback.answer()


# ══════════════════════════════════════════════════════════════
# SETTINGS — CALLBACKS (FIXED FOR BAD REQUEST)
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "settings_language")
async def settings_language(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.language_selection)

    try:
        await callback.message.edit_text(
            get_text("language.prompt", lang),
            reply_markup=language_switch_kb(lang),
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: types.CallbackQuery, state: FSMContext):
    """Back to settings — show reply keyboard (from inline language selection)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(MenuSection.settings)

    # Delete inline message, send new message with reply keyboard
    try:
        await callback.message.delete()
    except Exception:
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    await callback.message.answer(
        get_text("settings.title", lang),
        reply_markup=ColoredKeyboard.reply_settings_menu(lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_logout")
async def settings_logout(callback: types.CallbackQuery, state: FSMContext):
    """Logout callback — backward compat for old inline messages."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    # Delete inline message
    try:
        await callback.message.delete()
    except Exception:
        pass

    await _do_logout(callback.message, state, lang)
    await callback.answer()


@router.callback_query(F.data == "settings_ai_toggle")
async def settings_ai_toggle(callback: types.CallbackQuery, state: FSMContext):
    """AI toggle callback — backward compat for old inline messages."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    success, status_text = await _toggle_ai_core(state, lang, fallback_user_id=callback.from_user.id)
    await callback.answer(status_text, show_alert=True)

    # Delete inline message, send new message with reply keyboard
    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        get_text("settings.title", lang),
        reply_markup=ColoredKeyboard.reply_settings_menu(lang=lang),
    )


# ══════════════════════════════════════════════════════════════
# ADMIN CONTACT SESSION — FIX FOR STUCK STATE
# ══════════════════════════════════════════════════════════════

@router.message(
    F.chat.type == "private",
    F.content_type.in_({"text", "photo", "voice", "document", "video", "sticker"}),
    StateFilter(MenuSection.contact_admin),
)
async def handle_admin_contact_session(message: types.Message, state: FSMContext):
    """Save user message to backend admin_messages table.

    Exits contact_admin mode if user presses any menu button.
    """
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    # Agarda foydalanuvchi menyu tugmalaridan birini bossa, Admin sessiyadan chiqaramiz
    if message.text in MENU_BUTTONS:
        registration_complete = user_data.get("registration_complete", False)
        if registration_complete:
            await state.set_state(RegisteredSection.main_menu)
        else:
            await state.set_state(StartSection.main_menu)

        await message.answer(
            get_text("main_menu", lang),
            reply_markup=ColoredKeyboard.reply_main_menu(lang=lang),
        )
        return

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
                await message.answer(get_text("admin.sent_inbox", lang))
            else:
                await message.answer(get_text("admin.sent", lang))
    except Exception as e:
        print(f"[ADMIN SAVE ERROR] {e}")
        await message.answer(get_text("admin.sent", lang))
