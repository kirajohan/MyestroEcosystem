"""
Reminder Worker — vaqti kelgan eslatmalarni yuboradi.
Har 30 sekundda DB ni tekshiradi va due_at <= now bo'lganlarni yuboradi.
Daily/Weekly eslatmalar uchun keyingi vaqtni avtomatik hisoblaydi.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.reminder import Reminder

logger = logging.getLogger(__name__)


class ReminderWorker:
    """Background worker for reminders."""
    
    def __init__(self, bot, session_factory: async_sessionmaker[AsyncSession]):
        self.bot = bot
        self.session_factory = session_factory
        self.running = False
        self.check_interval = 30  # sekund
    
    async def start(self):
        """Worker'ni ishga tushirish."""
        self.running = True
        logger.info("🔔 ReminderWorker started")
        
        # ✅ BIRINCHI TEKSHIRUV DARHOL (kutmasdan)
        try:
            await self._process_due_reminders()
        except Exception as e:
            logger.error(f"❌ Initial check failed: {e}", exc_info=True)
        
        # Keyin har check_interval sekundda tekshirish
        while self.running:
            try:
                await asyncio.sleep(self.check_interval)
                await self._process_due_reminders()
            except asyncio.CancelledError:
                logger.info("🔕 ReminderWorker cancelled")
                break
            except Exception as e:
                logger.error(f"❌ ReminderWorker error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Xatodan keyin qisqa kutish
    
    def stop(self):
        """Worker'ni to'xtatish."""
        self.running = False
        logger.info("🔕 ReminderWorker stopped")
    
    async def _process_due_reminders(self):
        """Vaqti kelgan eslatmalarni qayta ishlash."""
        now = datetime.now(timezone.utc)
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(Reminder).where(
                    Reminder.is_active == True,
                    Reminder.due_at <= now,
                )
            )
            reminders = result.scalars().all()
            
            if not reminders:
                logger.debug(f"ℹ️ No due reminders at UTC {now.strftime('%H:%M:%S')}")
                return
            
            logger.info(f"🔔 Processing {len(reminders)} due reminder(s) at UTC {now.strftime('%H:%M:%S')}")
            
            for reminder in reminders:
                try:
                    await self._send_reminder(reminder)
                    
                    if reminder.reminder_type == "once":
                        reminder.is_active = False
                        logger.info(f"✅ One-time reminder {reminder.id} completed")
                    
                    elif reminder.reminder_type == "daily":
                        reminder.due_at = reminder.due_at + timedelta(days=1)
                        logger.info(f"🔄 Daily reminder {reminder.id} rescheduled to {reminder.due_at}")
                    
                    elif reminder.reminder_type == "weekly":
                        reminder.due_at = reminder.due_at + timedelta(weeks=1)
                        logger.info(f"🔄 Weekly reminder {reminder.id} rescheduled to {reminder.due_at}")
                    
                    reminder.last_sent_at = now
                
                except Exception as e:
                    logger.error(f"❌ Failed to process reminder {reminder.id}: {e}", exc_info=True)
            
            await session.commit()
    
    async def _send_reminder(self, reminder: Reminder):
        """Eslatmani user'ga yuborish."""
        # User'ning telegram_id sini olish
        from sqlalchemy import select
        from app.models.user import User
        
        async with self.session_factory() as session:
            result = await session.execute(
                select(User.telegram_id).where(User.id == reminder.user_id)
            )
            telegram_id = result.scalar_one_or_none()
        
        if not telegram_id:
            logger.warning(f"⚠️ User {reminder.user_id} not found for reminder {reminder.id}")
            return
        
        # Xabar formati
        type_icons = {
            "once": "1️⃣",
            "daily": "🔁",
            "weekly": "📅",
        }
        
        icon = type_icons.get(reminder.reminder_type, "⏰")
        
        text = (
            f"{icon} <b>ESLATMA</b>\n\n"
            f"📝 {reminder.text}\n\n"
            f"<i>⏰ Vaqti keldi!</i>"
        )
        
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=text,
                parse_mode="HTML",
            )
            logger.info(f"✅ Reminder {reminder.id} sent to user {telegram_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send reminder {reminder.id}: {e}")
