"""
Eslatmalar (Reminders) handler.
User /settings → ⏰ Eslatmalar orqali boshqaradi.
"""
import re
import logging
from datetime import datetime, timedelta, timezone
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.models.user import User
from app.models.reminder import Reminder
from bot.states.reminder_states import ReminderFSM
from bot.states.registration import MenuSection, RegisteredSection
from bot.keyboards.reply import (
    reminders_main_kb, 
    reminder_type_kb, 
    reminder_day_kb, 
    registered_menu_kb,
    remove_keyboard,
)
from bot.utils.i18n import get_text



router = Router()
logger = logging.getLogger(__name__)



async def _get_db_user_id(telegram_id: int, session: AsyncSession) -> int | None:
    """Telegram ID orqali DB'dan user ID olish."""
    result = await session.execute(
        select(User.id).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


# Hafta kunlari mapping (O'zbek/Rus/Ingliz → 0-6)
DAY_MAPPING = {
    # O'zbek
    "dushanba": 0, "seshanba": 1, "chorshanba": 2, "payshanba": 3,
    "juma": 4, "shanba": 5, "yakshanba": 6,
    # Rus
    "понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3,
    "пятница": 4, "суббота": 5, "воскресенье": 6,
    # Ingliz
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")


def _parse_time(time_str: str) -> tuple[int, int] | None:
    """HH:MM yoki HH MM formatini parse qiladi. Returns (hour, minute) yoki None."""
    # HH:MM
    match = re.match(r"^(\d{1,2}):(\d{2})$", time_str.strip())
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
    
    # HH MM (bo'sh joy bilan)
    match = re.match(r"^(\d{1,2})\s+(\d{2})$", time_str.strip())
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return h, m
    
    # Faqat soat (HH)
    match = re.match(r"^(\d{1,2})$", time_str.strip())
    if match:
        h = int(match.group(1))
        if 0 <= h <= 23:
            return h, 0
    
    return None


from datetime import datetime, timedelta, timezone
import pytz  # yoki zoneinfo

# Toshkent timezone
TASHKENT_TZ = pytz.timezone("Asia/Tashkent")  # UTC+5

def _calculate_next_due(
    reminder_type: str,
    hour: int,
    minute: int,
    day_of_week: int | None = None,
) -> datetime:
    """Keyingi due_at (UTC) ni hisoblaydi — Toshkent vaqti asosida."""
    
    # Hozirgi vaqt Toshkent timezone'da
    now_tashkent = datetime.now(TASHKENT_TZ)
    
    if reminder_type == "once":
        # Bugun yoki ertaga Toshkent vaqtida
        target_tashkent = now_tashkent.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_tashkent <= now_tashkent:
            target_tashkent += timedelta(days=1)
        # UTC ga convert qilish
        return target_tashkent.astimezone(timezone.utc)
    
    elif reminder_type == "daily":
        target_tashkent = now_tashkent.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_tashkent <= now_tashkent:
            target_tashkent += timedelta(days=1)
        return target_tashkent.astimezone(timezone.utc)
    
    elif reminder_type == "weekly":
        target_tashkent = now_tashkent.replace(hour=hour, minute=minute, second=0, microsecond=0)
        days_ahead = day_of_week - now_tashkent.weekday()
        if days_ahead < 0 or (days_ahead == 0 and target_tashkent <= now_tashkent):
            days_ahead += 7
        target_tashkent += timedelta(days=days_ahead)
        return target_tashkent.astimezone(timezone.utc)
    
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
    
    await state.set_state(MenuSection.settings)  # Settings ichida qoladi
    
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
    
    # ✅ DB'dan user ID olish
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
    
    # Ro'yxatni formatlash
    texts_header = {
        "uz": f"📋 Sizda <b>{len(reminders)}</b> ta aktiv eslatma bor:\n\n",
        "ru": f"📋 У вас <b>{len(reminders)}</b> активных напоминаний:\n\n",
        "en": f"📋 You have <b>{len(reminders)}</b> active reminders:\n\n",
    }
    
    response = texts_header.get(lang, texts_header["uz"])
    
    type_labels = {
        "once": {"uz": "1️⃣", "ru": "1️⃣", "en": "1️⃣"},
        "daily": {"uz": "🔁", "ru": "🔁", "en": "🔁"},
        "weekly": {"uz": "📅", "ru": "📅", "en": "📅"},
    }
    
    day_names = {
        "uz": ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"],
        "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "en": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    }
    
    for i, r in enumerate(reminders[:10], 1):  # Max 10 ta
        icon = type_labels.get(r.reminder_type, {}).get(lang, "⏰")
        text_short = r.text[:50] + "..." if len(r.text) > 50 else r.text
        
        # Vaqtni ko'rsatish
        due_local = r.due_at.astimezone()  # User'ning lokal vaqti
        time_str = due_local.strftime("%H:%M")
        date_str = due_local.strftime("%d.%m.%Y")
        
        if r.reminder_type == "weekly" and r.day_of_week is not None:
            day_label = day_names.get(lang, day_names["uz"])[r.day_of_week]
            time_info = f"{day_label} {time_str}"
        elif r.reminder_type == "daily":
            time_info = f"{time_str} ({'har kuni' if lang == 'uz' else 'daily'})"
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
    
    # ✅ DB'dan user ID olish
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
    """Matn qabul qilindi → tur tanlash."""
    text = message.text.strip()
    
    if len(text) > 500:
        await message.answer("⚠️ Matn juda uzun (max 500 belgi). Qisqaroq yozing.")
        return
    
    await state.update_data(reminder_text=text)
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    await state.set_state(ReminderFSM.waiting_type)
    
    texts = {
        "uz": f"📝 Eslatma: <i>{text}</i>\n\nQanday takrorlanishi kerak?",
        "ru": f"📝 Напоминание: <i>{text}</i>\n\nКак часто повторять?",
        "en": f"📝 Reminder: <i>{text}</i>\n\nHow often should it repeat?",
    }
    
    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminder_type_kb(lang),
        parse_mode="HTML",
    )


@router.message(ReminderFSM.waiting_type)
async def process_reminder_type(message: Message, state: FSMContext):
    """Tur tanlandi."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    text = message.text
    
    # Tur aniqlash
    if any(w in text for w in ["Bir martalik", "Одноразовое", "One-time", "1️⃣"]):
        reminder_type = "once"
    elif any(w in text for w in ["Har kuni", "Каждый день", "Daily", "🔁"]):
        reminder_type = "daily"
    elif any(w in text for w in ["Har hafta", "Каждую неделю", "Weekly", "📅"]):
        reminder_type = "weekly"
    elif "Orqaga" in text or "Назад" in text or "Back" in text:
        await state.clear()
        await message.answer(
            get_text("main_menu", lang),
            reply_markup=registered_menu_kb(lang),
        )
        return
    else:
        await message.answer("❌ Noto'g'ri tanlov. Iltimos, tugmalardan birini tanlang.")
        return
    
    await state.update_data(reminder_type=reminder_type)
    
    if reminder_type == "weekly":
        # Haftaning kunini so'rash
        await state.set_state(ReminderFSM.waiting_day)
        texts = {
            "uz": "📅 Haftaning qaysi kunida eslatish kerak?",
            "ru": "📅 В какой день недели напомнить?",
            "en": "📅 Which day of the week?",
        }
        await message.answer(
            texts.get(lang, texts["uz"]),
            reply_markup=reminder_day_kb(lang),
        )
    else:
        # Vaqtni so'rash
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


@router.message(ReminderFSM.waiting_day)
async def process_reminder_day(message: Message, state: FSMContext):
    """Hafta kuni tanlandi."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    text = message.text.lower()
    
    if "orqaga" in text or "назад" in text or "back" in text:
        await state.set_state(ReminderFSM.waiting_type)
        await message.answer(
            "Turga qaytdik. Qaysi tur?",
            reply_markup=reminder_type_kb(lang),
        )
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
async def process_reminder_time(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    """Vaqt qabul qilindi → eslatmani saqlash."""
    # Fayl boshida
    from datetime import datetime, timedelta, timezone

    # Toshkent UTC+5 (doimiy)
    TASHKENT_OFFSET = timedelta(hours=5)

    def _to_tashkent(utc_dt: datetime) -> datetime:
        """UTC datetime'ni Toshkent vaqtiga o'girish."""
        return utc_dt + TASHKENT_OFFSET

    
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    # ✅ DB'dan user ID olish (eng ishonchli usul)
    db_user_id = await _get_db_user_id(message.from_user.id, session)
    
    if not db_user_id:
        await message.answer(get_text("error.user_not_found", lang))
        await state.clear()
        return
    
    time_str = message.text.strip()
    parsed = _parse_time(time_str)
    
    if not parsed:
        await message.answer(
            "❌ Noto'g'ri vaqt formati.\n\n"
            "Iltimos, <b>HH:MM</b> formatida yozing.\n"
            "Masalan: <code>15:30</code>, <code>9:00</code>, <code>08:15</code>",
            parse_mode="HTML",
        )
        return
    
    hour, minute = parsed
    
    reminder_text = user_data.get("reminder_text")
    reminder_type = user_data.get("reminder_type")
    day_of_week = user_data.get("day_of_week")
    
    # Keyingi due_at ni hisoblash
    due_at = _calculate_next_due(reminder_type, hour, minute, day_of_week)
    scheduled_time = f"{hour:02d}:{minute:02d}"
    
    # DB ga saqlash
    reminder = Reminder(
        user_id=db_user_id,
        text=reminder_text,
        reminder_type=reminder_type,
        due_at=due_at,
        scheduled_time=scheduled_time,
        day_of_week=day_of_week,
        is_active=True,
    )
    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)
    
    # State tozalash
    await state.set_state(MenuSection.settings)
    
    # Muvaffaqiyat xabari
    type_label = {
        "once": {"uz": "Bir martalik", "ru": "Одноразовое", "en": "One-time"},
        "daily": {"uz": "Har kuni", "ru": "Каждый день", "en": "Daily"},
        "weekly": {"uz": "Har hafta", "ru": "Каждую неделю", "en": "Weekly"},
    }
    
    due_local = _to_tashkent(due_at)    
    
    texts = {
        "uz": (
            f"✅ <b>Eslatma yaratildi!</b>\n\n"
            f"📝 Matn: <i>{reminder_text}</i>\n"
            f"🔄 Tur: {type_label[reminder_type]['uz']}\n"
            f"⏰ Vaqt: <b>{due_local.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"Belgilangan vaqtda sizga xabar yuboraman."
        ),
        "ru": (
            f"✅ <b>Напоминание создано!</b>\n\n"
            f"📝 Текст: <i>{reminder_text}</i>\n"
            f"🔄 Тип: {type_label[reminder_type]['ru']}\n"
            f"⏰ Время: <b>{due_local.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"В указанное время я пришлю вам сообщение."
        ),
        "en": (
            f"✅ <b>Reminder created!</b>\n\n"
            f"📝 Text: <i>{reminder_text}</i>\n"
            f"🔄 Type: {type_label[reminder_type]['en']}\n"
            f"⏰ Time: <b>{due_local.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"I'll send you a message at the scheduled time."
        ),
    }
    
    await message.answer(
        texts.get(lang, texts["uz"]),
        reply_markup=reminders_main_kb(lang),
        parse_mode="HTML",
    )
    
    logger.info(f"✅ Reminder created: id={reminder.id}, user={db_user_id}, type={reminder_type}")


# ═══════════════════════════════════════════════════════════
# BEKOR QILISH
# ═══════════════════════════════════════════════════════════

@router.message(
    StateFilter(
        ReminderFSM.waiting_text,
        ReminderFSM.waiting_type,
        ReminderFSM.waiting_time,
        ReminderFSM.waiting_day,
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