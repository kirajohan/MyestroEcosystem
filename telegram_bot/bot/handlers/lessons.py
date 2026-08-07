# bot/handlers/lessons.py
"""Lessons handler — combined Video + File lessons menu with colored keyboards."""

from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.states.registration import LessonsStates, RegisteredSection
from bot.keyboards.inline import main_menu_kb
from bot.utils.i18n import get_text
import httpx

from bot.config import API_BASE_URL

router = Router()

# ─── Helpers ─────────────────────────────────────────────────

def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")


LIMIT = 5


async def fetch_content_list(content_type: str, page: int):
    """Fetch paginated content from backend.

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
    """Build paginated inline keyboard for content items — colored."""
    builder = InlineKeyboardBuilder()

    # Each item as button — Blue
    prefix = "video" if content_type == "video" else "file"
    for i, item in enumerate(items, 1):
        title = item.get("title", f"{prefix.capitalize()} #{i}")
        idx = (page - 1) * LIMIT + i
        label = f"#{idx}. {title}"
        
        builder.add(
            InlineKeyboardButton(
                text=label,
                callback_data=f"{prefix}_select_{item['id']}",
            )
        )

    # Navigation buttons
    total_pages = max(1, (total + LIMIT - 1) // LIMIT)
    nav_builder = InlineKeyboardBuilder()

    if page > 1:
        nav_builder.add(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"content:{content_type}:page_{page - 1}",
            )
        )

    nav_builder.add(
        InlineKeyboardButton(
            text=f"📄 {page}/{total_pages}",
            callback_data="noop"
        )
    )

    if page < total_pages:
        nav_builder.add(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"content:{content_type}:page_{page + 1}",
            )
        )

    # Back button
    back_texts = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
    nav_builder.add(
        InlineKeyboardButton(
            text=back_texts.get(lang, back_texts["uz"]),
            callback_data="back_to_lessons",
        )
    )

    # Combine all buttons
    for btn in nav_builder.buttons:
        builder.add(btn)

    builder.adjust(1, 3, 1)  # Content items (1 per row), navigation (3), back (1)
    return builder.as_markup()


async def send_content_list(target, content_type: str, page: int, lang: str, edit: bool = False):
    """Send or edit content list."""
    items, total = await fetch_content_list(content_type, page)

    if not items:
        text_key = "video.not_found" if content_type == "video" else "file.not_found"
        if edit and hasattr(target, 'edit_text'):
            await target.edit_text(get_text(text_key, lang))
            await target.edit_reply_markup(reply_markup=None)
        else:
            await target.answer(get_text(text_key, lang))
        return

    header = "🎬 Video darslar" if content_type == "video" else "📁 Fayl darslar"
    text = f"<b>{header}</b>\n\nKerakli darsni tanlang:"
    keyboard = build_content_keyboard(items, content_type, page, total, lang)

    if edit and hasattr(target, 'edit_text'):
        await target.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=keyboard, parse_mode="HTML")


def _lessons_submenu_keyboard(lang: str = "uz") -> InlineKeyboardBuilder:
    """Build lessons type selection keyboard — colored."""
    builder = InlineKeyboardBuilder()
    
    video_texts = {"uz": "🎬 Video darslar", "ru": "🎬 Видео уроки", "en": "🎬 Video lessons"}
    file_texts = {"uz": "📁 Fayl darslar", "ru": "📁 Файлы уроков", "en": "📁 File lessons"}
    back_texts = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
    
    builder.add(
        InlineKeyboardButton(
            text=video_texts.get(lang, video_texts["uz"]),
            callback_data="lessons_video",
        ),
        InlineKeyboardButton(
            text=file_texts.get(lang, file_texts["uz"]),
            callback_data="lessons_file",
        ),
    )
    
    builder.add(
        InlineKeyboardButton(
            text=back_texts.get(lang, back_texts["uz"]),
            callback_data="back_to_menu",
        )
    )
    
    builder.adjust(1, 1, 1)
    return builder.as_markup()


# ─── Reply Keyboard Handler ──────────────────────────────────

@router.message(or_f(
    F.text.in_(["📚 Darslar", "📚 Уроки", "📚 Lessons"]),
    Command("lessons"),
))
async def lessons_menu(message: types.Message, state: FSMContext):
    """Handle 📚 Lessons button — show inline sub-menu with Video/File options."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(LessonsStates.selecting_type)

    prompt_texts = {
        "uz": "📚 *Darslar*\n\nQaysi turdagi darslarni o'rganmoqchisiz?",
        "ru": "📚 *Уроки*\n\nКакой тип урока вас интересует?",
        "en": "📚 *Lessons*\n\nWhich type of lessons would you like?",
    }

    await message.answer(
        prompt_texts.get(lang, prompt_texts["uz"]),
        parse_mode="Markdown",
        reply_markup=_lessons_submenu_keyboard(lang),  # ✅ Colored
    )


# ─── Inline Callbacks ────────────────────────────────────────

@router.callback_query(F.data == "menu_lessons")
async def cb_menu_lessons(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'menu_lessons' callback from other inline menus (e.g. test results)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(LessonsStates.selecting_type)

    prompt_texts = {
        "uz": "📚 *Darslar*\n\nQaysi turdagi darslarni o'rganmoqchisiz?",
        "ru": "📚 *Уроки*\n\nКакой тип урока вас интересует?",
        "en": "📚 *Lessons*\n\nWhich type of lessons would you like?",
    }

    await callback.message.edit_text(
        prompt_texts.get(lang, prompt_texts["uz"]),
        parse_mode="Markdown",
        reply_markup=_lessons_submenu_keyboard(lang),  # ✅ Colored
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_lessons")
async def back_to_lessons(callback: types.CallbackQuery, state: FSMContext):
    """Back to lessons sub-menu from content list."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(LessonsStates.selecting_type)

    prompt_texts = {
        "uz": "📚 *Darslar*\n\nQaysi turdagi darslarni o'rganmoqchisiz?",
        "ru": "📚 *Уроки*\n\nКакой тип урока вас интересует?",
        "en": "📚 *Lessons*\n\nWhich type of lessons would you like?",
    }

    await callback.message.edit_text(
        prompt_texts.get(lang, prompt_texts["uz"]),
        parse_mode="Markdown",
        reply_markup=_lessons_submenu_keyboard(lang),  # ✅ Colored
    )
    await callback.answer()


@router.callback_query(F.data == "lessons_video")
async def lessons_video(callback: types.CallbackQuery, state: FSMContext):
    """Show video lessons list (paginated) — with confirmation."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(LessonsStates.viewing_lessons)

    await callback.message.edit_text("⏳ Video darslar yükleniyor...")
    await send_content_list(callback.message, "video", 1, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data == "lessons_file")
async def lessons_file(callback: types.CallbackQuery, state: FSMContext):
    """Show file lessons list (paginated) — with confirmation."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(LessonsStates.viewing_lessons)

    await callback.message.edit_text("⏳ Fayl darslar yükleniyor...")
    await send_content_list(callback.message, "file", 1, lang, edit=True)
    await callback.answer()


# ─── Content Pagination ──────────────────────────────────────

@router.callback_query(F.data.startswith("content:video:page_"))
async def content_video_page(callback: types.CallbackQuery, state: FSMContext):
    """Video lessons pagination."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    page = int(callback.data.split("_")[-1])
    await send_content_list(callback.message, "video", page, lang, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("content:file:page_"))
async def content_file_page(callback: types.CallbackQuery, state: FSMContext):
    """File lessons pagination."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    page = int(callback.data.split("_")[-1])
    await send_content_list(callback.message, "file", page, lang, edit=True)
    await callback.answer()


# ─── Content Selection (send video/file to user) ─────────────

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
                        await callback.message.answer_video(
                            video=tg_file_id,
                            caption=text,
                            parse_mode="HTML"
                        )
                        # Show continuation option
                        await callback.message.answer(
                            get_text("lessons.continue_prompt", lang),
                            reply_markup=_continue_lessons_keyboard(lang),
                        )
                    else:
                        error_texts = {
                            "uz": "❌ Video hali tayyor emas",
                            "ru": "❌ Видео еще не готово",
                            "en": "❌ Video is not ready yet"
                        }
                        await callback.message.answer(text + f"\n\n{error_texts.get(lang, error_texts['uz'])}")
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
                        await callback.message.answer_document(
                            document=tg_file_id,
                            caption=text,
                            parse_mode="HTML"
                        )
                        # Show continuation option
                        await callback.message.answer(
                            get_text("lessons.continue_prompt", lang),
                            reply_markup=_continue_lessons_keyboard(lang),
                        )
                    else:
                        error_texts = {
                            "uz": "❌ Fayl hali tayyor emas",
                            "ru": "❌ Файл еще не готов",
                            "en": "❌ File is not ready yet"
                        }
                        await callback.message.answer(text + f"\n\n{error_texts.get(lang, error_texts['uz'])}")
                else:
                    await callback.message.answer(get_text("file.not_found", lang))
            else:
                await callback.message.answer(get_text("file.not_found", lang))
    except Exception as e:
        print(f"[FILE SEND ERROR] {e}")
        await callback.message.answer(get_text("file.not_found", lang))

    await callback.answer()


# ─── Continue Lessons Helper ─────────────────────────────────

def _continue_lessons_keyboard(lang: str = "uz") -> InlineKeyboardBuilder:
    """Build continuation keyboard after selecting a lesson."""
    builder = InlineKeyboardBuilder()
    
    more_texts = {"uz": "📚 Boshqa darslar", "ru": "📚 Другие уроки", "en": "📚 More lessons"}
    back_texts = {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "en": "⬅️ Back"}
    
    builder.add(
        InlineKeyboardButton(
            text=more_texts.get(lang, more_texts["uz"]),
            callback_data="back_to_lessons",
        ),
        InlineKeyboardButton(
            text=back_texts.get(lang, back_texts["uz"]),
            callback_data="back_to_menu",
        ),
    )
    
    builder.adjust(1, 1)
    return builder.as_markup()