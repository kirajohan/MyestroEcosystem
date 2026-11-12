"""
Reminder Worker — vaqti kelgan eslatmalarni yuboradi.
Har 30 sekundda DB ni tekshiradi va due_at <= now bo'lganlarni yuboradi.
Daily/Weekly eslatmalar uchun keyingi vaqtni avtomatik hisoblaydi.
"""
import asyncio
import html
import logging
import re
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.reminder import Reminder
from bot.utils.ai_html import split_html, to_telegram_html

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
                select(User.telegram_id, User.cefr_level, User.lang, User.role).where(User.id == reminder.user_id)
            )
            row = result.first()

        if not row or not row.telegram_id:
            logger.warning(f"⚠️ User {reminder.user_id} not found for reminder {reminder.id}")
            return
        telegram_id, cefr_level, lang = row.telegram_id, row.cefr_level, row.lang

        # AI-generatsiya: prompt'ni matn sifatida emas, AI orqali bajarib yuboramiz
        if reminder.is_ai_generated:
            prompt = reminder.ai_prompt or reminder.text
            body = await self._generate_ai_content(
                prompt, cefr_level, lang, user_id=reminder.user_id, role=row.role,
            )
            if not body:
                body = f"⚠️ Kontent yaratib bo'lmadi. Keyingi safar qayta uriniladi.\n\n📝 {prompt}"
            text = f"🤖 <b>AI ESLATMA</b>\n\n{to_telegram_html(body)}"
        else:
            type_icons = {
                "once": "1️⃣",
                "daily": "🔁",
                "weekly": "📅",
            }
            icon = type_icons.get(reminder.reminder_type, "⏰")
            text = (
                f"{icon} <b>ESLATMA</b>\n\n"
                f"📝 {html.escape(reminder.text or '')}\n\n"
                f"<i>⏰ Vaqti keldi!</i>"
            )

        text = split_html(text, 4000)[0]  # teg-xavfsiz qisqartirish
        try:
            try:
                await self.bot.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
            except Exception as e:
                # AI yaroqsiz HTML yozgan bo'lishi mumkin — oddiy matn sifatida qayta urinish
                if "parse entities" not in str(e).lower():
                    raise
                await self.bot.send_message(chat_id=telegram_id, text=re.sub(r"<[^>]+>", "", text))
            logger.info(f"✅ Reminder {reminder.id} sent to user {telegram_id}")
        except Exception as e:
            logger.error(f"❌ Failed to send reminder {reminder.id}: {e}")

    async def _generate_ai_content(
        self, prompt: str, cefr_level: str | None, lang: str | None,
        user_id: int | None = None, role: str | None = None,
    ) -> str | None:
        """AI prompt'ni bajarib, tayyor kontent qaytaradi (xato bo'lsa None)."""
        from bot.utils.ai_client import ask_ai

        level = cefr_level or "A1"

        # Tool'li agent: hisobot/statistika kabi DB ma'lumoti kerak bo'lgan promptlar uchun
        if user_id:
            try:
                from app.services.admin_ai_service import AIToolsService
                from app.services.ai_agent import AIAgent
                from app.services.ai_extra_tools import WRITE_TOOL_NAMES

                is_admin = role in ("admin", "superadmin")
                async with self.session_factory() as session:
                    tools_service = AIToolsService(db=session, current_user_id=user_id, is_admin=is_admin)
                    agent = AIAgent(tools_service, is_admin=is_admin)
                    # Rekursiv eslatma yaratilmasligi uchun eslatma tool'lari olib tashlanadi
                    agent.tools = [
                        t for t in agent.tools
                        if t["function"]["name"] not in ("create_reminder", "delete_reminder", "list_my_reminders", *WRITE_TOOL_NAMES)
                    ]
                    answer = await agent.chat(
                        prompt,
                        additional_context=(
                            "Bu rejalashtirilgan eslatma — vaqti keldi. So'rovni HOZIR bajar va tayyor natijani ber. "
                            "Eslatma yaratma, savol berma, 'yuboraman' deb va'da qilma. "
                            f"Foydalanuvchining CEFR darajasi: {level}. 'Mening darajam' shu daraja."
                        ),
                    )
                if answer and not answer.startswith(("⚠️", "❌")):
                    return answer
            except Exception as e:
                logger.error(f"❌ Agent content generation failed, falling back: {e}", exc_info=True)

        system_prompt = (
            "Sen Myestro platformasining ingliz tili o'qituvchisisan. "
            "Foydalanuvchi so'ragan kontentni DARHOL yarat — savol berma, va'da qilma. "
            f"Foydalanuvchining CEFR darajasi: {level}. 'Mening darajam' deganda shu daraja nazarda tutiladi. "
            "Tushuntirishlar o'zbek tilida, inglizcha so'zlar <i>...</i> ichida. "
            "Faqat Telegram HTML teglaridan foydalan: <b>, <i>, <code>, <blockquote>. "
            "Markdown (**, #) ishlatma. Javob 3500 belgidan oshmasin."
        )
        try:
            return await ask_ai(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=1500,
            )
        except Exception as e:
            logger.error(f"❌ AI content generation failed: {e}", exc_info=True)
            return None
