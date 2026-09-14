"""
Eslatmalar (Reminders) handler.
User /settings → ⏰ Eslatmalar orqali boshqaradi.

Oqim:
  Matn → Tur → [Kun (once) / Hafta kuni (weekly)] → Vaqt → Saqlash
"""
import re
import logging
from datetime import datetime, timedelta, timezone, date

import pytz
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.user import User
from app.models.reminder import Reminder
from bot.states.reminder_states import ReminderFSM
from bot.states.registration import MenuSection
from bot.keyboards.reply import (
    reminders_main_kb,
    reminder_type_kb,
    reminder_day_kb,
    reminder_date_kb,
    registered_menu_kb,
    remove_keyboard,
    reminder_ai_choice_kb,  

)
from bot.utils.i18n import get_text

router = Router()
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TIMEZONE — Toshkent (UTC+5, DST yo'q)
# ═══════════════════════════════════════════════════════════
TASHKENT_TZ = pytz.timezone("Asia/Tashkent")
TASHKENT_OFFSET = timedelta(hours=5)


def _to_tashkent(utc_dt: datetime) -> datetime:
    """UTC datetime'ni Toshkent vaqtiga o'girish (ko'rsatish uchun, ishonchli)."""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(timezone.utc) + TASHKENT_OFFSET


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

async def _get_db_user_id(telegram_id: int, session: AsyncSession) -> int | None:
    """Telegram ID orqali DB'dan user ID olish."""
    result = await session.execute(
        select(User.id).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")


# Hafta kunlari mapping (O'zbek/Rus/Ingliz → 0-6, 0=Dushanba)
DAY_MAPPING = {
    "dushanba": 0, "seshanba": 1, "chorshanba": 2, "payshanba": 3,
    "juma": 4, "shanba": 5, "yakshanba": 6,
    "понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3,
    "пятница": 4, "суббота": 5, "воскресенье": 6,
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def _parse_time(time_str: str) -> tuple[int, int] | None:
    """HH:MM / HH.MM / HH,MM / HH MM / HH formatini parse qiladi."""
    time_str = time_str.strip()

    # HH:MM yoki HH.MM yoki HH,MM
    match = re.match(r"^(\d{1,2})[:.,](\d{2})$", time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m

    # HH MM (bo'sh joy bilan)
    match = re.match(r"^(\d{1,2})\s+(\d{2})$", time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m

    # Faqat soat (HH)
    match = re.match(r"^(\d{1,2})$", time_str)
    if match:
        h = int(match.group(1))
        if 0 <= h <= 23:
            return h, 0

    return None


def _parse_date(date_str: str) -> date | None:
    """DD.MM.YYYY formatini parse qilish."""
    match = re.match(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$", date_str.strip())
    if match:
        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return date(year, month, day)
        except ValueError:
            return None
    return None


def _calculate_next_due(
    reminder_type: str,
    hour: int,
    minute: int,
    day_of_week: int | None = None,
) -> datetime:
    """Keyingi due_at (UTC) ni hisoblaydi — Toshkent vaqti asosida."""
    now_tashkent = datetime.now(TASHKENT_TZ)

    if reminder_type in ("once", "daily"):
        target = now_tashkent.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now_tashkent:
            target += timedelta(days=1)
        return target.astimezone(timezone.utc)

    elif reminder_type == "weekly":
        target = now_tashkent.replace(hour=hour, minute=minute, second=0, microsecond=0)
        days_ahead = (day_of_week or 0) - now_tashkent.weekday()
        if days_ahead < 0 or (days_ahead == 0 and target <= now_tashkent):
            days_ahead += 7
        target += timedelta(days=days_ahead)
        return target.astimezone(timezone.utc)

    return datetime.now(timezone.utc)


# ═══════════════════════════════════════════════════════════
# ASOSIY MENYU
# ═══════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["⏰ Eslatmalar", "⏰ Напоминания", "⏰ Reminders"]),
)
async def open_reminders_menu(message: Message, state: FSMContext):
    """Eslatmalar menyusini ochish."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await state.set_state(MenuSection.settings)

    texts = {
        "uz": "⏰ <b>Eslatmalar</b>\n\nNima qilmoqchisiz?",
        "ru": "⏰ <b>Напоминания</b>\n\nЧто хотите сделать?",
        "en": "⏰ <b>Reminders</b>\n\nWhat would you like to do?",
    }

    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminders_main_kb(lang),
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════
# RO'YXATNI KO'RISH
# ═══════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["📋 Mening eslatmalarim", "📋 Мои напоминания", "📋 My reminders"]),
)
async def list_reminders(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    """Foydalanuvchining barcha aktiv eslatmalarini ko'rsatish."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    db_user_id = await _get_db_user_id(message.from_user.id, session)
    if not db_user_id:
        await message.answer(get_text("error.user_not_found", lang))
        return

    result = await session.execute(
        select(Reminder)
        .where(
            Reminder.user_id == db_user_id,
            Reminder.is_active == True,
        )
        .order_by(Reminder.due_at.asc())
    )
    reminders = result.scalars().all()

    if not reminders:
        texts = {
            "uz": "📭 Sizda aktiv eslatmalar yo'q.\n\nYangi eslatma yaratish uchun '➕ Yangi eslatma' tugmasini bosing.",
            "ru": "📭 У вас нет активных напоминаний.\n\nНажмите '➕ Новое напоминание', чтобы создать.",
            "en": "📭 You have no active reminders.\n\nClick '➕ New reminder' to create one.",
        }
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=reminders_main_kb(lang),
        )
        return

    headers = {
        "uz": f"📋 Sizda <b>{len(reminders)}</b> ta aktiv eslatma bor:\n\n",
        "ru": f"📋 У вас <b>{len(reminders)}</b> активных напоминаний:\n\n",
        "en": f"📋 You have <b>{len(reminders)}</b> active reminders:\n\n",
    }
    response = headers.get(lang, headers["uz"])

    type_icons = {"once": "1️⃣", "daily": "🔁", "weekly": "📅"}
    day_names = {
        "uz": ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"],
        "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "en": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    }
    daily_label = {"uz": "har kuni", "ru": "каждый день", "en": "daily"}

    for i, r in enumerate(reminders[:10], 1):
        icon = type_icons.get(r.reminder_type, "⏰")
        text_short = r.text[:50] + "..." if len(r.text) > 50 else r.text

        # ✅ Toshkent vaqtida ko'rsatish
        due_local = _to_tashkent(r.due_at)
        time_str = due_local.strftime("%H:%M")
        date_str = due_local.strftime("%d.%m.%Y")

        if r.reminder_type == "weekly" and r.day_of_week is not None:
            day_label = day_names.get(lang, day_names["uz"])[r.day_of_week]
            time_info = f"{day_label} {time_str}"
        elif r.reminder_type == "daily":
            time_info = f"{time_str} ({daily_label.get(lang, 'daily')})"
        else:
            time_info = f"{date_str} {time_str}"

        response += f"{icon} <b>{i}.</b> {text_short}\n    ⏱ <i>{time_info}</i>\n\n"

    if len(reminders) > 10:
        response += f"\n<i>...va yana {len(reminders) - 10} ta</i>"

    await message.answer(
        response,
        reply_markup=reminders_main_kb(lang),
        parse_mode="HTML",
    )


# ═══════════════════════════════════════════════════════════
# BARCHASINI O'CHIRISH
# ═══════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["🗑️ Barchasini o'chirish", "🗑️ Удалить все", "🗑️ Delete all"]),
)
async def delete_all_reminders(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    """Barcha aktiv eslatmalarni o'chirish."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    db_user_id = await _get_db_user_id(message.from_user.id, session)
    if not db_user_id:
        await message.answer(get_text("error.user_not_found", lang))
        return

    result = await session.execute(
        delete(Reminder).where(
            Reminder.user_id == db_user_id,
            Reminder.is_active == True,
        )
    )
    await session.commit()

    texts = {
        "uz": f"✅ {result.rowcount} ta eslatma o'chirildi.",
        "ru": f"✅ Удалено {result.rowcount} напоминаний.",
        "en": f"✅ Deleted {result.rowcount} reminders.",
    }

    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminders_main_kb(lang),
    )


# ═══════════════════════════════════════════════════════════
# YANGI ESLATMA YARATISH — FSM
# ═══════════════════════════════════════════════════════════

@router.message(
    F.text.in_(["➕ Yangi eslatma", "➕ Новое напоминание", "➕ New reminder"]),
)
async def start_new_reminder(message: Message, state: FSMContext):
    """Yangi eslatma yaratishni boshlash."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await state.set_state(ReminderFSM.waiting_text)

    texts = {
        "uz": "✏️ <b>Yangi eslatma</b>\n\nNima haqida eslatish kerak?\n\n<i>Misol: Dori ichish, Uchrashuv, Ingliz tili mashq qilish</i>",
        "ru": "✏️ <b>Новое напоминание</b>\n\nО чём напомнить?\n\n<i>Пример: Принять лекарство, Встреча, Заниматься английским</i>",
        "en": "✏️ <b>New reminder</b>\n\nWhat should I remind you about?\n\n<i>Example: Take medicine, Meeting, Practice English</i>",
    }

    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=remove_keyboard,
        parse_mode="HTML",
    )


@router.message(ReminderFSM.waiting_text, F.text)
async def process_reminder_text(message: Message, state: FSMContext):
    """Matn qabul qilindi → AI yoki statik tanlash."""
    text = message.text.strip()
    
    if len(text) > 500:
        await message.answer("⚠️ Matn juda uzun (max 500 belgi).")
        return
    
    await state.update_data(reminder_text=text)
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    # ⭐ YANGI: AI tanlash qadami
    await state.set_state(ReminderFSM.waiting_ai_choice)
    
    texts = {
        "uz": (
            f"📝 Eslatma matni: <i>{text}</i>\n\n"
            f"Qanday yuborilsin?"
        ),
        "ru": (
            f"📝 Текст напоминания: <i>{text}</i>\n\n"
            f"Как отправлять?"
        ),
        "en": (
            f"📝 Reminder text: <i>{text}</i>\n\n"
            f"How should it be sent?"
        ),
    }
    
    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminder_ai_choice_kb(lang),
        parse_mode="HTML",
    )



@router.message(ReminderFSM.waiting_type)
async def process_reminder_type(message: Message, state: FSMContext):
    """Tur tanlandi."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    text = message.text

    if any(w in text for w in ["Bir martalik", "Одноразовое", "One-time", "1️⃣"]):
        reminder_type = "once"
    elif any(w in text for w in ["Har kuni", "Каждый день", "Daily", "🔁"]):
        reminder_type = "daily"
    elif any(w in text for w in ["Har hafta", "Каждую неделю", "Weekly", "📅"]):
        reminder_type = "weekly"
    elif "Orqaga" in text or "Назад" in text or "Back" in text:
        await state.clear()
        await message.answer(get_text("main_menu", lang), reply_markup=registered_menu_kb(lang))
        return
    else:
        await message.answer("❌ Noto'g'ri tanlov.")
        return

    await state.update_data(reminder_type=reminder_type)

    if reminder_type == "once":
        # Bir martalik → kun tanlash
        await state.set_state(ReminderFSM.waiting_date)
        texts = {
            "uz": "📅 Qaysi kunda eslatish kerak?",
            "ru": "📅 В какой день напомнить?",
            "en": "📅 Which day should I remind you?",
        }
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=reminder_date_kb(lang),
        )

    elif reminder_type == "weekly":
        # Haftalik → hafta kuni tanlash
        await state.set_state(ReminderFSM.waiting_day)
        texts = {
            "uz": "📅 Haftaning qaysi kunida?",
            "ru": "📅 В какой день недели?",
            "en": "📅 Which day of the week?",
        }
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=reminder_day_kb(lang),
        )

    else:  # daily
        await state.set_state(ReminderFSM.waiting_time)
        texts = {
            "uz": "⏰ Soat nechida?\n\n<i>Format: HH:MM (masalan: 15:30)</i>",
            "ru": "⏰ Во сколько?\n\n<i>Формат: HH:MM (например: 15:30)</i>",
            "en": "⏰ What time?\n\n<i>Format: HH:MM (example: 15:30)</i>",
        }
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=remove_keyboard,
            parse_mode="HTML",
        )


@router.message(ReminderFSM.waiting_date)
async def process_reminder_date(message: Message, state: FSMContext):
    """Bir martalik uchun kun tanlash (Bugun / Ertaga / Boshqa kun)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    text = message.text

    if "Orqaga" in text or "Назад" in text or "Back" in text:
        await state.set_state(ReminderFSM.waiting_type)
        await message.answer("Turga qaytdik.", reply_markup=reminder_type_kb(lang))
        return

    if any(w in text for w in ["Bugun", "Сегодня", "Today"]):
        target_date = date.today()
    elif any(w in text for w in ["Ertaga", "Завтра", "Tomorrow"]):
        target_date = date.today() + timedelta(days=1)
    elif any(w in text for w in ["Boshqa kun", "Другой день", "Another day"]):
        # Boshqa kun — sana kiritishni so'rash
        await state.update_data(waiting_custom_date=True)
        texts = {
            "uz": "📝 Sanani kiriting.\n\n<i>Format: DD.MM.YYYY (masalan: 20.09.2026)</i>",
            "ru": "📝 Введите дату.\n\n<i>Формат: DD.MM.YYYY (например: 20.09.2026)</i>",
            "en": "📝 Enter the date.\n\n<i>Format: DD.MM.YYYY (example: 20.09.2026)</i>",
        }
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=remove_keyboard,
            parse_mode="HTML",
        )
        return
    else:
        # Ehtimol user to'g'ridan-to'g'ri sana yozgan
        parsed_date = _parse_date(text)
        if parsed_date:
            target_date = parsed_date
        else:
            await message.answer("❌ Iltimos, tugmalardan birini tanlang yoki sana kiriting.")
            return

    # ✅ MUHIM: custom date flag'ni tozalash
    await state.update_data(
        target_date=target_date.isoformat(),
        waiting_custom_date=False,
    )
    await state.set_state(ReminderFSM.waiting_time)

    texts = {
        "uz": f"📅 Sana: <b>{target_date.strftime('%d.%m.%Y')}</b>\n\n⏰ Soat nechida?\n\n<i>Format: HH:MM</i>",
        "ru": f"📅 Дата: <b>{target_date.strftime('%d.%m.%Y')}</b>\n\n⏰ Во сколько?\n\n<i>Формат: HH:MM</i>",
        "en": f"📅 Date: <b>{target_date.strftime('%d.%m.%Y')}</b>\n\n⏰ What time?\n\n<i>Format: HH:MM</i>",
    }
    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=remove_keyboard,
        parse_mode="HTML",
    )


@router.message(ReminderFSM.waiting_day)
async def process_reminder_day(message: Message, state: FSMContext):
    """Hafta kuni tanlandi (weekly uchun)."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    text = message.text.lower()

    if "orqaga" in text or "назад" in text or "back" in text:
        await state.set_state(ReminderFSM.waiting_type)
        await message.answer("Turga qaytdik. Qaysi tur?", reply_markup=reminder_type_kb(lang))
        return

    day_of_week = DAY_MAPPING.get(text)
    if day_of_week is None:
        await message.answer("❌ Noto'g'ri kun. Iltimos, tugmalardan birini tanlang.")
        return

    await state.update_data(day_of_week=day_of_week)
    await state.set_state(ReminderFSM.waiting_time)

    texts = {
        "uz": "⏰ Soat nechida eslatish kerak?\n\n<i>Format: HH:MM (masalan: 15:30)</i>",
        "ru": "⏰ Во сколько напомнить?\n\n<i>Формат: HH:MM (например: 15:30)</i>",
        "en": "⏰ What time should I remind you?\n\n<i>Format: HH:MM (example: 15:30)</i>",
    }
    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=remove_keyboard,
        parse_mode="HTML",
    )


@router.message(ReminderFSM.waiting_time, F.text)
async def process_reminder_time(message: Message, state: FSMContext, session: AsyncSession):
    """Vaqt qabul qilindi → eslatmani saqlash."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    db_user_id = await _get_db_user_id(message.from_user.id, session)
    if not db_user_id:
        await message.answer(get_text("error.user_not_found", lang))
        await state.clear()
        return

    # Custom date tekshirish
    if user_data.get("waiting_custom_date"):
        parsed_date = _parse_date(message.text)
        if parsed_date:
            await state.update_data(
                target_date=parsed_date.isoformat(),
                waiting_custom_date=False,
            )
            texts = {
                "uz": f"📅 Sana: <b>{parsed_date.strftime('%d.%m.%Y')}</b>\n\n⏰ Soat nechida?",
                "ru": f"📅 Дата: <b>{parsed_date.strftime('%d.%m.%Y')}</b>\n\n⏰ Во сколько?",
                "en": f"📅 Date: <b>{parsed_date.strftime('%d.%m.%Y')}</b>\n\n⏰ What time?",
            }
            await message.answer(
                texts.get(lang, texts["uz"]),
                reply_markup=remove_keyboard,
                parse_mode="HTML",
            )
            return
        else:
            await message.answer("❌ Noto'g'ri sana. DD.MM.YYYY formatida yozing.")
            return

    time_str = message.text.strip()
    parsed = _parse_time(time_str)
    if not parsed:
        await message.answer("❌ Noto'g'ri vaqt. HH:MM formatida yozing.", parse_mode="HTML")
        return

    hour, minute = parsed
    
    # FSM'dan barcha ma'lumotlarni olish
    reminder_text = user_data.get("reminder_text")
    reminder_type = user_data.get("reminder_type")
    day_of_week = user_data.get("day_of_week")
    target_date_str = user_data.get("target_date")
    is_ai_generated = user_data.get("is_ai_generated", False)
    ai_prompt = user_data.get("ai_prompt")

    # AI reminder uchun text = ai_prompt bo'ladi
    if is_ai_generated and ai_prompt:
        reminder_text = ai_prompt

    # due_at hisoblash
    if reminder_type == "once" and target_date_str:
        target_date = date.fromisoformat(target_date_str)
        now_tashkent = datetime.now(TASHKENT_TZ)
        target_tashkent = TASHKENT_TZ.localize(
            datetime(target_date.year, target_date.month, target_date.day, hour, minute, 0)
        )
        if target_tashkent <= now_tashkent:
            await message.answer("⚠️ Bu vaqt allaqachon o'tgan.")
            return
        due_at = target_tashkent.astimezone(timezone.utc)
    else:
        due_at = _calculate_next_due(reminder_type, hour, minute, day_of_week)

    scheduled_time = f"{hour:02d}:{minute:02d}"

    # ✅ DB'ga saqlash — yangi maydonlar bilan
    reminder = Reminder(
        user_id=db_user_id,
        text=reminder_text,
        reminder_type=reminder_type,
        due_at=due_at,
        scheduled_time=scheduled_time,
        day_of_week=day_of_week,
        is_active=True,
        is_ai_generated=is_ai_generated,
        ai_prompt=ai_prompt,
    )
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)

    await state.set_state(MenuSection.settings)

    # Muvaffaqiyat xabari
    due_local = _to_tashkent(due_at)
    type_labels = {
        "once": {"uz": "Bir martalik", "ru": "Одноразовое", "en": "One-time"},
        "daily": {"uz": "Har kuni", "ru": "Каждый день", "en": "Daily"},
        "weekly": {"uz": "Har hafta", "ru": "Каждую неделю", "en": "Weekly"},
    }
    type_label = type_labels.get(reminder_type, {}).get(lang, reminder_type)

    # AI yoki statik ko'rsatish
    if is_ai_generated:
        content_type_label = {
            "uz": "🤖 AI har kuni yangi content yaratadi",
            "ru": "🤖 AI будет создавать новый контент каждый раз",
            "en": "🤖 AI will generate new content each time",
        }
        content_line = content_type_label.get(lang, content_type_label["uz"])
        display_text = ai_prompt
    else:
        content_line = ""
        display_text = reminder_text

    texts = {
        "uz": (
            f"✅ <b>Eslatma yaratildi!</b>\n\n"
            f"📝 Matn: <i>{display_text}</i>\n"
            f"{content_line}\n"
            f"🔄 Tur: {type_label}\n"
            f"⏰ Vaqt: <b>{due_local.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"Belgilangan vaqtda sizga xabar yuboraman."
        ),
        "ru": (
            f"✅ <b>Напоминание создано!</b>\n\n"
            f"📝 Текст: <i>{display_text}</i>\n"
            f"{content_line}\n"
            f"🔄 Тип: {type_label}\n"
            f"⏰ Время: <b>{due_local.strftime('%d.%m.%Y %H:%M')}</b>"
        ),
        "en": (
            f"✅ <b>Reminder created!</b>\n\n"
            f"📝 Text: <i>{display_text}</i>\n"
            f"{content_line}\n"
            f"🔄 Type: {type_label}\n"
            f"⏰ Time: <b>{due_local.strftime('%d.%m.%Y %H:%M')}</b>"
        ),
    }

    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminders_main_kb(lang),
        parse_mode="HTML",
    )
    
    logger.info(
        f"✅ Reminder created: id={reminder.id}, user={db_user_id}, "
        f"type={reminder_type}, ai_generated={is_ai_generated}"
    )

    
# ═══════════════════════════════════════════════════════════
# BEKOR QILISH
# ═══════════════════════════════════════════════════════════

@router.message(ReminderFSM.waiting_ai_choice)
async def process_reminder_ai_choice(message: Message, state: FSMContext):
    """AI generatsiya yoki statik matn tanlash."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    text = message.text
    
    if "Orqaga" in text or "Назад" in text or "Back" in text:
        await state.set_state(ReminderFSM.waiting_text)
        await message.answer("Matn qayta kiriting:")
        return
    
    # AI yoki statik aniqlash
    is_ai = any(w in text for w in ["AI", "🤖", "yangi", "новый", "new"])
    
    if is_ai:
        await state.update_data(is_ai_generated=True)
        await state.set_state(ReminderFSM.waiting_ai_prompt)
        
        texts = {
            "uz": (
                "🤖 <b>AI Prompt</b>\n\n"
                "AI ga qanday content yaratish kerakligini ayting.\n\n"
                "<b>Misollar:</b>\n"
                "• Mening B1 darajam uchun 10 ta yangi so'z yubor\n"
                "• Har kuni bitta inglizcha idiomani tushuntir\n"
                "• Grammar bo'yicha bitta maslahat ber\n"
                "• Bugungi kun uchun motivasiya"
            ),
            "ru": (
                "🤖 <b>AI Prompt</b>\n\n"
                "Скажите AI, какой контент создавать.\n\n"
                "<b>Примеры:</b>\n"
                "• Пришли 10 новых слов для моего уровня B1\n"
                "• Каждый день объясняй одну идиому\n"
                "• Давай совет по грамматике"
            ),
            "en": (
                "🤖 <b>AI Prompt</b>\n\n"
                "Tell AI what content to create.\n\n"
                "<b>Examples:</b>\n"
                "• Send me 10 new words for my B1 level\n"
                "• Explain one idiom every day\n"
                "• Give me a grammar tip"
            ),
        }
        
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=remove_keyboard,
            parse_mode="HTML",
        )
    else:
        # Statik matn — eski flow
        await state.update_data(is_ai_generated=False)
        await state.set_state(ReminderFSM.waiting_type)
        
        reminder_text = user_data.get("reminder_text")
        texts = {
            "uz": f"📝 Eslatma: <i>{reminder_text}</i>\n\nQanday takrorlanishi kerak?",
            "ru": f"📝 Напоминание: <i>{reminder_text}</i>\n\nКак часто повторять?",
            "en": f"📝 Reminder: <i>{reminder_text}</i>\n\nHow often?",
        }
        
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=reminder_type_kb(lang),
            parse_mode="HTML",
        )


@router.message(
    StateFilter(
        ReminderFSM.waiting_text,
        ReminderFSM.waiting_type,
        ReminderFSM.waiting_time,
        ReminderFSM.waiting_day,
        ReminderFSM.waiting_date,
    ),
    F.text.in_(["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back", "/cancel"]),
)
async def cancel_reminder_creation(message: Message, state: FSMContext):
    """FSM ni bekor qilish."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    await state.clear()

    texts = {
        "uz": "❌ Eslatma yaratish bekor qilindi.",
        "ru": "❌ Создание напоминания отменено.",
        "en": "❌ Reminder creation cancelled.",
    }

    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminders_main_kb(lang),
    )