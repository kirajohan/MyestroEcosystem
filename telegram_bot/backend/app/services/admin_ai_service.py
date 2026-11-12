"""
Universal AI Agent Service
Admin va user uchun — role-based access bilan butun DB ni ko'radi.
OpenRouter Function Calling orqali ishlaydi.
"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
import pytz
from sqlalchemy import select, func, desc, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# ═══════════════════════════════════════════════════════════
# MODELS IMPORT
# ═══════════════════════════════════════════════════════════
from app.models.user import User
from app.models.exam import (
    Exam,
    ExamBlock,
    ExamItem,
    ExamOption,
    ExamAttempt,
    ExamAttemptBlock,
    ExamAnswer,
    ExamAIJob,
)
from app.models.conversation import ConversationThread, Message
from app.models.content import ContentItem
from app.models.broadcast import BroadcastJob, BroadcastHistory
from app.models.inbox import InboxMessage, InboxMessageHistory
from app.models.logs import ErrorLog, AuditLog, ApiLog
from app.models.settings import SystemSetting
from app.services.ai_extra_tools import AIExtraToolsMixin, EXTRA_ADMIN_TOOLS, EXTRA_USER_TOOLS

logger = logging.getLogger(__name__)


from app.models.reminder import Reminder 

# ═══════════════════════════════════════════════════════════
# TIMEZONE + REMINDER HELPERS (mustaqil, bot'dan import qilinmaydi)
# ═══════════════════════════════════════════════════════════
from datetime import datetime, timedelta, timezone, date as _date_class
import re

from app.models.reminder import Reminder
# from datetime import datetime, timedelta, timezone, date as _date_class

# ═══════════════════════════════════════════════════════════
# TIMEZONE + REMINDER HELPERS (modul darajasida)
# ═══════════════════════════════════════════════════════════
TASHKENT_TZ = pytz.timezone("Asia/Tashkent")
TASHKENT_OFFSET = timedelta(hours=5)


def _to_tashkent(utc_dt: datetime) -> datetime:
    """UTC datetime'ni Toshkent vaqtiga o'girish."""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(timezone.utc) + TASHKENT_OFFSET


def _parse_time_reminder(time_str: str):
    """HH:MM / HH.MM / HH formatini parse qilish."""
    time_str = (time_str or "").strip()
    
    # HH:MM yoki HH.MM yoki HH,MM
    match = re.match(r"^(\d{1,2})[:.,](\d{2})$", time_str)
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


def _calculate_next_due_reminder(
    reminder_type: str,
    hour: int,
    minute: int,
    day_of_week=None,
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

MAX_ACTIVE_REMINDERS = 20
MAX_ACTIVE_AI_REMINDERS = 5
MAX_AI_PROMPT_CHARS = 500


class AIToolsService(AIExtraToolsMixin):
    """
    Universal AI tool'lar to'plami.
    Har bir tool — bu DB'ga so'rov yuboruvchi funksiya.
    """

    def __init__(
        self,
        db: AsyncSession,
        current_user_id: int,
        is_admin: bool,
        pending_store=None,
        redis=None,
    ):
        self.db = db
        self.current_user_id = current_user_id
        self.is_admin = is_admin
        self.pending_store = pending_store  # yozish amallari uchun tasdiqlash ombori (faqat chat)
        self.redis = redis

    @staticmethod
    def _mask_phone(phone: Optional[str]) -> Optional[str]:
        """Telefonni LLM ga to'liq yubormaslik: +998 ** *** 12 34."""
        if not phone:
            return phone
        digits = re.sub(r"\D", "", str(phone))
        if len(digits) < 6:
            return "***"
        return f"+{digits[:3]} ** *** {digits[-4:-2]} {digits[-2:]}"

    async def _audit(self, action: str, resource: Optional[str] = None, details: Optional[Dict] = None) -> None:
        """Admin PII o'qish/yozish amallarini AuditLog'ga yozish (xato bo'lsa jimgina o'tadi)."""
        try:
            self.db.add(AuditLog(
                user_id=self.current_user_id,
                action=f"ai_agent.{action}",
                resource=resource,
                details=details or {},
                severity="info",
            ))
            await self.db.commit()
        except Exception as e:
            logger.warning(f"[AUDIT] yozib bo'lmadi: {type(e).__name__}")
            try:
                await self.db.rollback()
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════
    # DATABASE OVERVIEW — Butun baza ko'rinishi
    # ═══════════════════════════════════════════════════════════

    async def get_database_overview(self) -> Dict[str, Any]:
        """Barcha jadvallarning qisqacha ko'rinishi (faqat admin)."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        tables = {
            "users": User,
            "exams": Exam,
            "exam_blocks": ExamBlock,
            "exam_items": ExamItem,
            "exam_options": ExamOption,
            "exam_attempts": ExamAttempt,
            "exam_attempt_blocks": ExamAttemptBlock,
            "exam_answers": ExamAnswer,
            "exam_ai_jobs": ExamAIJob,
            "conversations": ConversationThread,
            "messages": Message,
            "content_items": ContentItem,
            "broadcast_jobs": BroadcastJob,
            "broadcast_history": BroadcastHistory,
            "inbox_messages": InboxMessage,
            "inbox_message_history": InboxMessageHistory,
            "error_logs": ErrorLog,
            "audit_logs": AuditLog,
            "api_logs": ApiLog,
            "system_settings": SystemSetting,
        }

        overview = {}
        for table_name, model in tables.items():
            try:
                count = await self.db.scalar(select(func.count(model.id)))
                overview[table_name] = count or 0
            except Exception as e:
                logger.warning(f"[overview] {table_name}: {type(e).__name__}")
                await self.db.rollback()
                overview[table_name] = "error"

        return {
            "database_overview": overview,
            "total_tables": len(tables),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    # ═══════════════════════════════════════════════════════════
    # USERS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_users_overview(self, days: int = 7) -> Dict[str, Any]:
        """Foydalanuvchilar statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total = await self.db.scalar(select(func.count(User.id))) or 0
        active = await self.db.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        ) or 0
        admins = await self.db.scalar(
            select(func.count(User.id)).where(User.role == "admin")
        ) or 0
        ai_enabled = await self.db.scalar(
            select(func.count(User.id)).where(User.ai_enabled == True)
        ) or 0

        since = datetime.now(timezone.utc) - timedelta(days=days)
        new_users = await self.db.scalar(
            select(func.count(User.id)).where(User.created_at >= since)
        ) or 0

        return {
            "total_users": total,
            "active_users": active,
            "admins": admins,
            "ai_enabled": ai_enabled,
            f"new_users_last_{days}_days": new_users,
        }

    async def list_users(
        self,
        limit: int = 20,
        offset: int = 0,
        search: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Foydalanuvchilar ro'yxati."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        query = select(User).order_by(desc(User.created_at))

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.telegram_username.ilike(search_pattern),
                    User.phone.ilike(search_pattern),
                )
            )
        if role:
            query = query.where(User.role == role)

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        users = result.scalars().all()
        await self._audit("list_users", "users", {"search": search, "role": role, "limit": limit, "offset": offset, "returned": len(users)})

        return {
            "users": [
                {
                    "id": u.id,
                    "telegram_id": u.telegram_id,
                    "full_name": u.full_name,
                    "username": u.telegram_username,                    
                    "phone": self._mask_phone(u.phone),
                    "role": u.role,
                    "cefr_level": u.cefr_level,
                    "ai_enabled": u.ai_enabled,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
            "count": len(users),
            "limit": limit,
            "offset": offset,
        }

    async def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """Aniq user haqida to'liq ma'lumot."""
        if not self.is_admin:
            if user_id != self.current_user_id:
                return {"error": "Ruxsat yo'q"}

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return {"error": "User topilmadi"}
        if self.is_admin and user_id != self.current_user_id:
            await self._audit("get_user_details", f"user:{user_id}")

        attempts_result = await self.db.execute(
            select(ExamAttempt)
            .where(ExamAttempt.user_id == user_id)
            .order_by(desc(ExamAttempt.created_at))
            .limit(20)
        )
        attempts = attempts_result.scalars().all()

        messages_result = await self.db.execute(
            select(func.count(Message.id))
            .join(ConversationThread)
            .where(ConversationThread.user_id == user_id)
        )
        message_count = messages_result.scalar() or 0

        return {
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "full_name": user.full_name,
                "username": user.telegram_username,                
                "phone": user.phone,
                "role": user.role,
                "cefr_level": user.cefr_level,
                "ai_enabled": user.ai_enabled,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "attempts_count": len(attempts),
            "recent_attempts": [
                {
                    "id": a.id,
                    "exam_id": a.exam_id,
                    "status": a.status,
                    "total_score": a.total_score,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in attempts[:10]
            ],
            "ai_messages_count": message_count,
        }

    async def search_users(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Ism, username yoki phone bo'yicha user qidirish."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        pattern = f"%{query}%"
        result = await self.db.execute(
            select(User)
            .where(
                or_(
                    User.full_name.ilike(pattern),
                    User.telegram_username.ilike(pattern),
                    User.phone.ilike(pattern),
                )
            )
            .limit(limit)
        )
        users = result.scalars().all()
        await self._audit("search_users", "users", {"query_len": len(query), "returned": len(users)})

        return {
            "results": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "username": u.telegram_username,                    
                    "role": u.role,
                    "cefr_level": u.cefr_level,
                }
                for u in users
            ],
            "count": len(users),
        }

    # ═══════════════════════════════════════════════════════════
    # EXAMS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_exams_overview(self) -> Dict[str, Any]:
        """Exam'lar statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total = await self.db.scalar(select(func.count(Exam.id))) or 0
        published = await self.db.scalar(
            select(func.count(Exam.id)).where(Exam.is_published == True)
        ) or 0

        type_result = await self.db.execute(
            select(Exam.exam_type, func.count(Exam.id)).group_by(Exam.exam_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        cefr_result = await self.db.execute(
            select(Exam.cefr_level, func.count(Exam.id)).group_by(Exam.cefr_level)
        )
        by_cefr = {row[0] or "unknown": row[1] for row in cefr_result.all()}

        return {
            "total_exams": total,
            "published_exams": published,
            "by_type": by_type,
            "by_cefr_level": by_cefr,
        }

    async def list_exams(
        self,
        exam_type: Optional[str] = None,
        cefr_level: Optional[str] = None,
        published_only: bool = False,
    ) -> Dict[str, Any]:
        """Exam'lar ro'yxati."""
        query = select(Exam).order_by(desc(Exam.created_at))

        if exam_type:
            query = query.where(Exam.exam_type == exam_type)
        if cefr_level:
            query = query.where(Exam.cefr_level == cefr_level)
        if published_only:
            query = query.where(Exam.is_published == True)

        if not self.is_admin:
            query = query.where(Exam.is_published == True)

        result = await self.db.execute(query.limit(50))
        exams = result.scalars().all()

        return {
            "exams": [
                {
                    "id": e.id,
                    "code": e.code,
                    "title": e.title,
                    "exam_type": e.exam_type,
                    "cefr_level": e.cefr_level,
                    "time_limit_sec": e.time_limit_sec,
                    "is_published": e.is_published,
                }
                for e in exams
            ],
            "count": len(exams),
        }

    async def get_exam_details(self, exam_id: int) -> Dict[str, Any]:
        """Exam + blocklar + itemlar."""
        result = await self.db.execute(
            select(Exam)
            .options(
                selectinload(Exam.blocks)
                .selectinload(ExamBlock.items)
                .selectinload(ExamItem.options)
            )
            .where(Exam.id == exam_id, *([] if self.is_admin else [Exam.is_published == True]))
        )
        exam = result.scalar_one_or_none()
        if not exam:
            return {"error": "Exam topilmadi"}

        return {
            "exam": {
                "id": exam.id,
                "code": exam.code,
                "title": exam.title,
                "exam_type": exam.exam_type,
                "cefr_level": exam.cefr_level,
                "is_published": exam.is_published,
            },
            "blocks": [
                {
                    "id": b.id,
                    "block_type": b.block_type,
                    "title": b.title,
                    "items_count": len(b.items),
                    "items": [
                        {
                            "id": i.id,
                            "item_type": i.item_type,
                            "title": i.title,
                            "options_count": len(i.options) if i.options else 0,
                            "max_score": i.max_score,
                        }
                        for i in sorted(b.items, key=lambda x: x.order)
                    ],
                }
                for b in sorted(exam.blocks, key=lambda x: x.order)
            ],
        }

    # ═══════════════════════════════════════════════════════════
    # ATTEMPTS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_attempts_overview(self) -> Dict[str, Any]:
        """Urinishlar statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total = await self.db.scalar(select(func.count(ExamAttempt.id))) or 0

        status_result = await self.db.execute(
            select(ExamAttempt.status, func.count(ExamAttempt.id))
            .group_by(ExamAttempt.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        avg_score = await self.db.scalar(
            select(func.avg(ExamAttempt.total_score))
            .where(ExamAttempt.status == "completed")
        )

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        today_count = await self.db.scalar(
            select(func.count(ExamAttempt.id))
            .where(ExamAttempt.created_at >= today)
        ) or 0

        return {
            "total_attempts": total,
            "by_status": by_status,
            "average_score": float(avg_score) if avg_score else 0,
            "today_attempts": today_count,
        }

    async def get_attempt_details(self, attempt_id: int) -> Dict[str, Any]:
        """Urinish + javoblar + AI feedback."""
        if self.is_admin:
            query = select(ExamAttempt).where(ExamAttempt.id == attempt_id)
        else:
            query = select(ExamAttempt).where(
                and_(
                    ExamAttempt.id == attempt_id,
                    ExamAttempt.user_id == self.current_user_id,
                )
            )

        result = await self.db.execute(
            query.options(
                selectinload(ExamAttempt.exam),
                selectinload(ExamAttempt.answers).selectinload(ExamAnswer.item),
            )
        )
        attempt = result.scalar_one_or_none()
        if not attempt:
            return {"error": "Urinish topilmadi yoki ruxsat yo'q"}

        return {
            "attempt": {
                "id": attempt.id,
                "user_id": attempt.user_id,
                "exam_title": attempt.exam.title if attempt.exam else None,
                "status": attempt.status,
                "total_score": attempt.total_score,
                "cefr_estimate": attempt.cefr_estimate,
                "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            },
            "answers": [
                {
                    "item_id": a.item_id,
                    "item_type": a.item.item_type if a.item else None,
                    "item_title": a.item.title if a.item else None,
                    "selected_options": a.selected_options,
                    "text_answer": a.text_answer,
                    "auto_score": a.auto_score,
                    "ai_score": a.ai_score,
                    "final_score": a.final_score,
                    "ai_status": a.ai_status,
                    "feedback": a.feedback,
                }
                for a in attempt.answers
            ],
        }

    # ═══════════════════════════════════════════════════════════
    # AI JOBS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_ai_jobs_overview(self) -> Dict[str, Any]:
        """AI joblar statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        status_result = await self.db.execute(
            select(ExamAIJob.status, func.count(ExamAIJob.id))
            .group_by(ExamAIJob.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        type_result = await self.db.execute(
            select(ExamAIJob.job_type, func.count(ExamAIJob.id))
            .group_by(ExamAIJob.job_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        return {
            "by_status": by_status,
            "by_type": by_type,
            "total": sum(by_status.values()),
        }

    async def get_ai_errors(self, limit: int = 10) -> Dict[str, Any]:
        """Oxirgi AI xatoliklari."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        result = await self.db.execute(
            select(ExamAIJob)
            .where(ExamAIJob.status == "error")
            .order_by(desc(ExamAIJob.updated_at))
            .limit(limit)
        )
        jobs = result.scalars().all()

        return {
            "errors": [
                {
                    "id": j.id,
                    "job_type": j.job_type,
                    "attempt_id": j.attempt_id,
                    "error_message": j.error_message[:300] if j.error_message else None,
                    "attempts_count": j.attempts_count,
                    "updated_at": j.updated_at.isoformat() if j.updated_at else None,
                }
                for j in jobs
            ],
            "count": len(jobs),
        }

    # ═══════════════════════════════════════════════════════════
    # CONTENT TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_content_overview(self) -> Dict[str, Any]:
        """Kontent statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total = await self.db.scalar(select(func.count(ContentItem.id))) or 0

        type_result = await self.db.execute(
            select(ContentItem.content_type, func.count(ContentItem.id))
            .group_by(ContentItem.content_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        return {
            "total_content": total,
            "by_type": by_type,
        }

    # ═══════════════════════════════════════════════════════════
    # REMINDER TOOLS
    # ═══════════════════════════════════════════════════════════

    async def create_reminder(
        self,
        text: str,
        reminder_type: str = "once",
        time: str = "",
        date: str = "",
        day_of_week: int | None = None,
        is_ai_generated: bool = False,
        ai_prompt: str | None = None,
    ) -> Dict[str, Any]:
        """Eslatma yaratish (oddiy yoki AI-generatsiya)."""
        date_str = date

        parsed_time = _parse_time_reminder(time) if time else None
        if not parsed_time:
            return {"error": "Vaqt formati noto'g'ri. HH:MM formatida yozing."}

        hour, minute = parsed_time

        # AI reminder uchun text = ai_prompt
        if is_ai_generated and ai_prompt:
            display_text = ai_prompt
        else:
            display_text = text

        if reminder_type == "once" and date_str:
            try:
                target_date = _date_class.fromisoformat(date_str)
            except ValueError:
                return {"error": "Sana formati noto'g'ri. YYYY-MM-DD formatida yozing."}
            now_tashkent = datetime.now(TASHKENT_TZ)
            target_tashkent = TASHKENT_TZ.localize(
                datetime(target_date.year, target_date.month, target_date.day, hour, minute, 0)
            )
            if target_tashkent <= now_tashkent:
                return {"error": "Bu vaqt allaqachon o'tgan."}
            due_at = target_tashkent.astimezone(timezone.utc)
        else:
            due_at = _calculate_next_due_reminder(reminder_type, hour, minute, day_of_week)

        # Cheklovlar: har bir AI-eslatma har safar LLM chaqiradi — nazoratsiz ko'paymasin
        if ai_prompt and len(ai_prompt) > MAX_AI_PROMPT_CHARS:
            return {"error": f"AI prompt juda uzun (max {MAX_AI_PROMPT_CHARS} belgi)."}
        active_total = await self.db.scalar(
            select(func.count(Reminder.id)).where(Reminder.user_id == self.current_user_id, Reminder.is_active == True)
        ) or 0
        if active_total >= MAX_ACTIVE_REMINDERS:
            return {"error": f"Aktiv eslatmalar limiti ({MAX_ACTIVE_REMINDERS}) to'lgan. Avval ba'zilarini o'chiring."}
        if is_ai_generated:
            active_ai = await self.db.scalar(
                select(func.count(Reminder.id)).where(
                    Reminder.user_id == self.current_user_id,
                    Reminder.is_active == True,
                    Reminder.is_ai_generated == True,
                )
            ) or 0
            if active_ai >= MAX_ACTIVE_AI_REMINDERS:
                return {"error": f"AI eslatmalar limiti ({MAX_ACTIVE_AI_REMINDERS}) to'lgan."}

        reminder = Reminder(
            user_id=self.current_user_id,
            text=display_text,
            reminder_type=reminder_type,
            due_at=due_at,
            scheduled_time=f"{hour:02d}:{minute:02d}",
            day_of_week=day_of_week,
            is_active=True,
            is_ai_generated=is_ai_generated,
            ai_prompt=ai_prompt,
        )
        self.db.add(reminder)
        await self.db.commit()
        await self.db.refresh(reminder)

        return {
            "status": "success",
            "reminder_id": reminder.id,
            "text": display_text,
            "type": reminder_type,
            "is_ai_generated": is_ai_generated,
            "due_at_local": _to_tashkent(due_at).strftime("%d.%m.%Y %H:%M"),
        }


    async def list_my_reminders(self) -> Dict[str, Any]:
        """Foydalanuvchining aktiv eslatmalari."""
        result = await self.db.execute(
            select(Reminder)
            .where(
                Reminder.user_id == self.current_user_id,
                Reminder.is_active == True,
            )
            .order_by(Reminder.due_at.asc())
            .limit(10)
        )
        reminders = result.scalars().all()

        return {
            "reminders": [
                {
                    "id": r.id,
                    "text": r.text[:100],
                    "type": r.reminder_type,
                    "scheduled_time": r.scheduled_time,
                    "due_at": _to_tashkent(r.due_at).strftime("%d.%m.%Y %H:%M"),
                }
                for r in reminders
            ],
            "count": len(reminders),
        }

    async def delete_reminder(self, reminder_id: int) -> Dict[str, Any]:
        """Eslatmani o'chirish."""
        result = await self.db.execute(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == self.current_user_id,
            )
        )
        reminder = result.scalar_one_or_none()

        if not reminder:
            return {"error": "Eslatma topilmadi yoki sizga tegishli emas."}

        reminder.is_active = False
        await self.db.commit()

        return {
            "status": "success",
            "message": f"Eslatma '{reminder.text[:50]}' o'chirildi.",
        }

    # ═══════════════════════════════════════════════════════════
    # MESSAGES / CONVERSATIONS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_messages_overview(self) -> Dict[str, Any]:
        """AI chat statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total_threads = await self.db.scalar(
            select(func.count(ConversationThread.id))
        ) or 0
        total_messages = await self.db.scalar(
            select(func.count(Message.id))
        ) or 0

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        today_messages = await self.db.scalar(
            select(func.count(Message.id)).where(Message.created_at >= today)
        ) or 0

        return {
            "total_conversations": total_threads,
            "total_messages": total_messages,
            "today_messages": today_messages,
        }

    # ═══════════════════════════════════════════════════════════
    # INBOX TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_inbox_overview(self) -> Dict[str, Any]:
        """Inbox statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total = await self.db.scalar(select(func.count(InboxMessage.id))) or 0
        new_count = await self.db.scalar(
            select(func.count(InboxMessage.id)).where(InboxMessage.status == "new")
        ) or 0
        replied_count = await self.db.scalar(
            select(func.count(InboxMessage.id)).where(InboxMessage.status == "replied")
        ) or 0
        closed_count = await self.db.scalar(
            select(func.count(InboxMessage.id)).where(InboxMessage.status == "closed")
        ) or 0

        return {
            "total_messages": total,
            "new": new_count,
            "replied": replied_count,
            "closed": closed_count,
        }

    async def list_inbox(
        self,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Inbox xabarlari ro'yxati."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        query = select(InboxMessage).order_by(desc(InboxMessage.created_at))

        if status:
            query = query.where(InboxMessage.status == status)

        result = await self.db.execute(query.limit(limit))
        messages = result.scalars().all()
        await self._audit("list_inbox", "inbox", {"status": status, "returned": len(messages)})

        return {
            "messages": [
                {
                    "id": m.id,
                    "user_id": m.user_id,
                    "subject": m.subject,
                    "user_message": m.user_message[:200] if m.user_message else None,
                    "status": m.status,
                    "is_read": m.is_read,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
            "count": len(messages),
        }

    # ═══════════════════════════════════════════════════════════
    # BROADCAST TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_broadcast_overview(self) -> Dict[str, Any]:
        """Broadcast statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        total_jobs = await self.db.scalar(select(func.count(BroadcastJob.id))) or 0
        total_sent = await self.db.scalar(select(func.count(BroadcastHistory.id))) or 0

        return {
            "total_broadcast_jobs": total_jobs,
            "total_messages_sent": total_sent,
        }

    # ═══════════════════════════════════════════════════════════
    # SYSTEM / LOGS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_error_logs(self, limit: int = 10) -> Dict[str, Any]:
        """Oxirgi xatolik loglari."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        result = await self.db.execute(
            select(ErrorLog)
            .order_by(desc(ErrorLog.created_at))
            .limit(limit)
        )
        logs = result.scalars().all()

        return {
            "errors": [
                {
                    "id": l.id,
                    "message": str(l.error_message)[:300] if l.error_message else None,
                    "service": l.service,
                    "error_type": l.error_type,
                    "is_fixed": l.is_fixed if hasattr(l, 'is_fixed') else None,
                    "created_at": l.created_at.isoformat() if l.created_at else None,
                }
                for l in logs
            ],
            "count": len(logs),
        }

    async def get_system_settings(self) -> Dict[str, Any]:
        """Tizim sozlamalari."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        result = await self.db.execute(select(SystemSetting))
        settings = result.scalars().all()

        return {
            "settings": [
                {
                    "key": s.key if hasattr(s, 'key') else str(s),
                    "value": s.value if hasattr(s, 'value') else None,
                }
                for s in settings
            ],
        }

    # ═══════════════════════════════════════════════════════════
    # ANALYTICS TOOLS
    # ═══════════════════════════════════════════════════════════

    async def get_cefr_distribution(self) -> Dict[str, Any]:
        """Foydalanuvchilar CEFR taqsimoti."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        result = await self.db.execute(
            select(User.cefr_level, func.count(User.id))
            .where(User.cefr_level.isnot(None))
            .group_by(User.cefr_level)
        )
        return {
            "distribution": {row[0]: row[1] for row in result.all()},
        }

    async def get_top_performers(self, limit: int = 10) -> Dict[str, Any]:
        """Eng yaxshi natija ko'rsatgan userlar."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        result = await self.db.execute(
            select(User, func.avg(ExamAttempt.total_score).label("avg_score"))
            .join(ExamAttempt)
            .where(ExamAttempt.status == "completed")
            .group_by(User.id)
            .order_by(desc("avg_score"))
            .limit(limit)
        )
        rows = result.all()

        return {
            "top_performers": [
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "cefr_level": user.cefr_level,
                    "average_score": round(float(avg_score), 2) if avg_score else 0,
                }
                for user, avg_score in rows
            ],
        }

    async def get_daily_stats(self) -> Dict[str, Any]:
        """Bugungi kun statistikasi."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)

        new_users = await self.db.scalar(
            select(func.count(User.id)).where(User.created_at >= today)
        ) or 0
        new_attempts = await self.db.scalar(
            select(func.count(ExamAttempt.id)).where(ExamAttempt.created_at >= today)
        ) or 0
        completed = await self.db.scalar(
            select(func.count(ExamAttempt.id)).where(
                and_(
                    ExamAttempt.status == "completed",
                    ExamAttempt.completed_at >= today,
                )
            )
        ) or 0
        ai_jobs_today = await self.db.scalar(
            select(func.count(ExamAIJob.id)).where(ExamAIJob.created_at >= today)
        ) or 0
        new_messages = await self.db.scalar(
            select(func.count(Message.id)).where(Message.created_at >= today)
        ) or 0

        return {
            "date": today.date().isoformat(),
            "new_users": new_users,
            "new_attempts": new_attempts,
            "completed_attempts": completed,
            "ai_jobs": ai_jobs_today,
            "messages": new_messages,
        }

    # ═══════════════════════════════════════════════════════════
    # SEARCH EVERYWHERE
    # ═══════════════════════════════════════════════════════════

    async def search_everywhere(self, query: str) -> Dict[str, Any]:
        """Universal qidiruv — user, exam, message."""
        if not self.is_admin:
            return {"error": "Ruxsat yo'q"}

        pattern = f"%{query}%"
        results = {"users": [], "exams": [], "messages": []}
        await self._audit("search_everywhere", "global", {"query_len": len(query)})

        user_result = await self.db.execute(
            select(User)
            .where(
                or_(
                    User.full_name.ilike(pattern),
                    User.telegram_username.ilike(pattern),
                    User.phone.ilike(pattern),
                )
            )
            .limit(10)
        )
        results["users"] = [
            {"id": u.id, "full_name": u.full_name, "username": u.telegram_username}
            for u in user_result.scalars().all()
        ]

        exam_result = await self.db.execute(
            select(Exam)
            .where(
                or_(
                    Exam.title.ilike(pattern),
                    Exam.code.ilike(pattern),
                )
            )
            .limit(10)
        )
        results["exams"] = [
            {"id": e.id, "title": e.title, "code": e.code, "type": e.exam_type}
            for e in exam_result.scalars().all()
        ]

        msg_result = await self.db.execute(
            select(Message)
            .where(Message.content.ilike(pattern))
            .order_by(desc(Message.created_at))
            .limit(10)
        )
        results["messages"] = [
            {
                "id": m.id,
                "content": m.content[:200] if m.content else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in msg_result.scalars().all()
        ]

        return results

    # ═══════════════════════════════════════════════════════════
    # USER SELF TOOLS (oddiy user uchun)
    # ═══════════════════════════════════════════════════════════

    async def get_my_profile(self) -> Dict[str, Any]:
        """Foydalanuvchining o'z profili."""
        result = await self.db.execute(
            select(User).where(User.id == self.current_user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return {"error": "User topilmadi"}

        return {
            "id": user.id,
            "full_name": user.full_name,
            "username": user.telegram_username,            
            "cefr_level": user.cefr_level,
            "ai_enabled": user.ai_enabled,
        }

    async def get_my_attempts(self, limit: int = 10) -> Dict[str, Any]:
        """Foydalanuvchining o'z urinishlari."""
        result = await self.db.execute(
            select(ExamAttempt)
            .options(selectinload(ExamAttempt.exam))
            .where(ExamAttempt.user_id == self.current_user_id)
            .order_by(desc(ExamAttempt.created_at))
            .limit(limit)
        )
        attempts = result.scalars().all()

        return {
            "attempts": [
                {
                    "id": a.id,
                    "exam_title": a.exam.title if a.exam else None,
                    "exam_type": a.exam.exam_type if a.exam else None,
                    "status": a.status,
                    "total_score": a.total_score,
                    "cefr_estimate": a.cefr_estimate,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in attempts
            ],
        }

    async def get_my_best_scores(self) -> Dict[str, Any]:
        """Har bir skill bo'yicha eng yaxshi natijalar."""
        result = await self.db.execute(
            select(
                Exam.exam_type,
                func.max(ExamAttempt.total_score).label("best_score"),
            )
            .join(ExamAttempt)
            .where(
                and_(
                    ExamAttempt.user_id == self.current_user_id,
                    ExamAttempt.status == "completed",
                )
            )
            .group_by(Exam.exam_type)
        )

        return {
            "best_scores": {
                row[0]: float(row[1]) if row[1] else 0
                for row in result.all()
            },
        }



# ══════════════════════════════════════════════════════════════
# TOOL SCHEMAS (OpenAI Function Calling format)
# ══════════════════════════════════════════════════════════════

ADMIN_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_database_overview",
            "description": "Butun ma'lumotlar bazasining qisqacha ko'rinishi — har bir jadvalda nechta qator borligini qaytaradi. Bu eng yaxshi boshlang'ich nuqta agar nima borligi haqida umumiy tushuncha kerak bo'lsa.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_users_overview",
            "description": "Foydalanuvchilar statistikasi: jami, faol, admin, AI yoqilgan, oxirgi N kundagi yangilar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Oxirgi necha kun uchun (default: 7)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_users",
            "description": "Foydalanuvchilar ro'yxati. Search, role bo'yicha filterlash mumkin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nechta user qaytarish (default: 20)"},
                    "offset": {"type": "integer", "description": "Offset (default: 0)"},
                    "search": {"type": "string", "description": "Ism, username yoki phone bo'yicha qidirish"},
                    "role": {"type": "string", "description": "Role bo'yicha filter (user/admin)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_details",
            "description": "Aniq bir foydalanuvchi haqida to'liq ma'lumot: profil, urinishlar, AI chat tarixi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Foydalanuvchi ID"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_users",
            "description": "Ism, username yoki telefon raqami bo'yicha foydalanuvchi qidirish.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Qidiruv matni"},
                    "limit": {"type": "integer", "description": "Maksimal natijalar soni (default: 10)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exams_overview",
            "description": "Exam'lar statistikasi: jami, published, turlar va CEFR bo'yicha taqsimot.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_exams",
            "description": "Exam'lar ro'yxati. Type va CEFR bo'yicha filterlash mumkin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "exam_type": {"type": "string", "description": "full/listening/reading/writing/speaking"},
                    "cefr_level": {"type": "string", "description": "A1/A2/B1/B2/C1/C2"},
                    "published_only": {"type": "boolean"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exam_details",
            "description": "Aniq exam haqida to'liq ma'lumot: blocklar, itemlar, variantlar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "exam_id": {"type": "integer"},
                },
                "required": ["exam_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_attempts_overview",
            "description": "Urinishlar statistikasi: jami, statuslar bo'yicha, o'rtacha ball, bugungi soni.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_attempt_details",
            "description": "Aniq urinish haqida to'liq ma'lumot: javoblar, ballar, AI feedback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "attempt_id": {"type": "integer"},
                },
                "required": ["attempt_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ai_jobs_overview",
            "description": "AI job'lar holati: status va turlar bo'yicha statistika.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_ai_errors",
            "description": "Oxirgi AI xatoliklari ro'yxati.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nechta xatolik (default: 10)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_content_overview",
            "description": "Kontent statistikasi: jami, turlar bo'yicha.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_messages_overview",
            "description": "AI chat statistikasi: suhbatlar, xabarlar, bugungi xabarlar.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_inbox_overview",
            "description": "Inbox statistikasi: yangi, javob berilgan, yopilgan xabarlar soni.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_inbox",
            "description": "Inbox xabarlari ro'yxati. Status bo'yicha filterlash mumkin (new/replied/closed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "new, replied, closed"},
                    "limit": {"type": "integer", "description": "Nechta xabar (default: 20)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_broadcast_overview",
            "description": "Broadcast statistikasi: jami joblar va yuborilgan xabarlar.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_error_logs",
            "description": "Oxirgi tizim xatolik loglari.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nechta log (default: 10)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_settings",
            "description": "Tizim sozlamalari ro'yxati.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cefr_distribution",
            "description": "Foydalanuvchilarning CEFR darajalari bo'yicha taqsimoti.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_performers",
            "description": "Eng yaxshi natija ko'rsatgan foydalanuvchilar (o'rtacha ball bo'yicha).",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Top N (default: 10)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_stats",
            "description": "Bugungi kun statistikasi: yangi userlar, urinishlar, xabarlar, AI jobs.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_everywhere",
            "description": "Universal qidiruv: user, exam, message bo'yicha bir vaqtda qidiradi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Qidiruv matni"},
                },
                "required": ["query"],
            },
        },
    },
]

USER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_my_profile",
            "description": "Mening profilim: ism, CEFR daraja, AI holati.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_attempts",
            "description": "Mening imtihon urinishlarim ro'yxati.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Nechta urinish (default: 10)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_best_scores",
            "description": "Har bir skill (listening/reading/writing/speaking) bo'yicha mening eng yaxshi natijalarim.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_attempt_details",
            "description": "Mening aniq bir urinishim haqida to'liq ma'lumot (faqat o'z urinishimni ko'ra olaman).",
            "parameters": {
                "type": "object",
                "properties": {
                    "attempt_id": {"type": "integer"},
                },
                "required": ["attempt_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_exams",
            "description": "Mavjud imtihonlar ro'yxati (faqat published).",
            "parameters": {
                "type": "object",
                "properties": {
                    "exam_type": {"type": "string"},
                    "cefr_level": {"type": "string"},
                },
            },
        },
    },
]

# ══════════════════════════════════════════════════════════════
# REMINDER TOOL SCHEMAS (OpenAI Function Calling format)
# ══════════════════════════════════════════════════════════════

REMINDER_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_reminder",
            "description": "Eslatma yaratish. Oddiy yoki AI-generatsiya qiladigan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Eslatma matni (statik bo'lsa)"},
                    "reminder_type": {
                        "type": "string",
                        "enum": ["once", "daily", "weekly"],
                    },
                    "time": {"type": "string", "description": "Vaqt HH:MM formatida"},
                    "date": {"type": "string", "description": "Sana YYYY-MM-DD (faqat once)"},
                    "day_of_week": {"type": "integer", "description": "0-6 (faqat weekly)"},
                    "is_ai_generated": {
                        "type": "boolean",
                        "description": "Agar TRUE bo'lsa, AI har safar yangi content yaratadi",
                    },
                    "ai_prompt": {
                        "type": "string",
                        "description": "AI uchun prompt (masalan: 'B1 daraja uchun 10 ta yangi so\\'z')",
                    },
                },
                "required": ["text", "reminder_type", "time"],
            },
        },
    },
        {
            "type": "function",
            "function": {
                "name": "list_my_reminders",
                "description": "Foydalanuvchining barcha aktiv eslatmalarini ko'rsatish. 'Eslatmalarim', 'qanday eslatmalar bor' deb so'ralganda ishlatiladi.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_reminder",
                "description": "Eslatmani o'chirish.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reminder_id": {"type": "integer", "description": "Eslatma ID raqami"},
                    },
                    "required": ["reminder_id"],
                },
            },
        },
]

# ✅ Ikkala ro'yxatga ham qo'shish (admin va user ikkalasi ham foydalanishi mumkin)
ADMIN_TOOLS = ADMIN_TOOLS + REMINDER_TOOL_SCHEMAS + EXTRA_ADMIN_TOOLS
USER_TOOLS = USER_TOOLS + REMINDER_TOOL_SCHEMAS + EXTRA_USER_TOOLS