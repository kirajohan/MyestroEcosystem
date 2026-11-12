"""
AI agent uchun qo'shimcha tool'lar (AIToolsService mixin):

 O'qish (admin):  get_exam_analytics, list_attempts, get_user_activity, list_content, get_usage_stats
 O'qish (user):   get_my_progress
 Yozish (admin):  set_user_ai_enabled, change_user_role, set_user_active, reply_inbox, close_inbox,
                  prepare_broadcast, create_reminder_for_user

Yozish tool'lari hech qachon to'g'ridan-to'g'ri bajarilmaydi: `prepare` bosqichi PendingAction
yaratadi, foydalanuvchi inline tugma bilan tasdiqlagandan keyingina `execute_pending` ishlaydi.
"""
import html as _html
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, desc, and_, or_

from app.models.user import User
from app.models.exam import Exam, ExamAttempt, ExamAttemptBlock, ExamBlock, ExamItem, ExamAnswer, ExamAIJob
from app.models.content import ContentItem
from app.models.inbox import InboxMessage, InboxMessageHistory
from app.models.logs import AuditLog

logger = logging.getLogger(__name__)

ASSIGNABLE_ROLES = ("student", "teacher", "admin")
PROTECTED_ROLES = ("superadmin",)
BROADCAST_MAX_CHARS = 3500
PREVIEW_CHARS = 160

# Tasdiqlash kerak bo'lgan yozish tool'lari (nazoratsiz ishlaydigan agentlardan olib tashlanadi)
WRITE_TOOL_NAMES = (
    "set_user_ai_enabled", "change_user_role", "set_user_active", "reply_inbox",
    "close_inbox", "prepare_broadcast", "create_reminder_for_user",
)

_DENY = {"error": "Ruxsat yo'q"}


def _iso(dt) -> Optional[str]:
    return dt.isoformat() if dt else None


class AIExtraToolsMixin:
    """AIToolsService uchun qo'shimcha tool'lar. self.db, self.is_admin, self.current_user_id, self._audit kerak."""

    pending_store: Any = None  # async create(action, params, summary) -> action_id
    redis: Any = None          # async redis (inbox/broadcast navbatlari uchun)

    # ═══════════════════════════════════════════════════════════
    # O'QISH — ADMIN
    # ═══════════════════════════════════════════════════════════

    async def get_exam_analytics(self, exam_id: int) -> Dict[str, Any]:
        """Exam bo'yicha: urinishlar, o'rtacha ball, CEFR taqsimoti, blok va eng qiyin savollar."""
        if not self.is_admin:
            return _DENY

        exam = (await self.db.execute(select(Exam).where(Exam.id == exam_id))).scalar_one_or_none()
        if not exam:
            return {"error": "Exam topilmadi"}

        total = await self.db.scalar(select(func.count(ExamAttempt.id)).where(ExamAttempt.exam_id == exam_id)) or 0
        scored = await self.db.scalar(
            select(func.count(ExamAttempt.id)).where(ExamAttempt.exam_id == exam_id, ExamAttempt.total_score.isnot(None))
        ) or 0
        avg_score = await self.db.scalar(
            select(func.avg(ExamAttempt.total_score)).where(ExamAttempt.exam_id == exam_id, ExamAttempt.total_score.isnot(None))
        )

        status_rows = await self.db.execute(
            select(ExamAttempt.status, func.count(ExamAttempt.id)).where(ExamAttempt.exam_id == exam_id).group_by(ExamAttempt.status)
        )
        cefr_rows = await self.db.execute(
            select(ExamAttempt.cefr_estimate, func.count(ExamAttempt.id))
            .where(ExamAttempt.exam_id == exam_id, ExamAttempt.cefr_estimate.isnot(None))
            .group_by(ExamAttempt.cefr_estimate)
        )
        block_rows = await self.db.execute(
            select(ExamBlock.block_type, func.avg(ExamAttemptBlock.score), func.count(ExamAttemptBlock.id))
            .join(ExamAttempt, ExamAttempt.id == ExamAttemptBlock.attempt_id)
            .join(ExamBlock, ExamBlock.id == ExamAttemptBlock.block_id)
            .where(ExamAttempt.exam_id == exam_id, ExamAttemptBlock.score.isnot(None))
            .group_by(ExamBlock.block_type)
        )

        score_expr = func.coalesce(ExamAnswer.final_score, ExamAnswer.ai_score, ExamAnswer.auto_score)
        hard_rows = await self.db.execute(
            select(
                ExamItem.id, ExamItem.title, ExamItem.item_type,
                func.avg(score_expr / func.nullif(ExamItem.max_score, 0)).label("ratio"),
                func.count(ExamAnswer.id),
            )
            .join(ExamBlock, ExamBlock.id == ExamItem.block_id)
            .join(ExamAnswer, ExamAnswer.item_id == ExamItem.id)
            .where(ExamBlock.exam_id == exam_id, score_expr.isnot(None))
            .group_by(ExamItem.id, ExamItem.title, ExamItem.item_type)
            .having(func.count(ExamAnswer.id) >= 3)
            .order_by("ratio")
            .limit(5)
        )

        await self._audit("get_exam_analytics", f"exam:{exam_id}")
        return {
            "exam": {"id": exam.id, "code": exam.code, "title": exam.title, "cefr_level": exam.cefr_level},
            "attempts_total": total,
            "attempts_scored": scored,
            "average_score": round(float(avg_score), 2) if avg_score is not None else None,
            "by_status": {s or "unknown": c for s, c in status_rows.all()},
            "cefr_estimates": {c: n for c, n in cefr_rows.all()},
            "avg_score_by_block_type": [
                {"block_type": t, "avg_score": round(float(a), 2), "count": n} for t, a, n in block_rows.all() if a is not None
            ],
            "hardest_items": [
                {"item_id": i, "title": (t or "")[:80], "item_type": it, "avg_score_ratio": round(float(r), 2), "answers": n}
                for i, t, it, r, n in hard_rows.all() if r is not None
            ],
        }

    async def list_attempts(
        self,
        exam_id: Optional[int] = None,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Urinishlar ro'yxati (exam yoki user bo'yicha filtr)."""
        if not self.is_admin:
            return _DENY
        query = select(ExamAttempt).order_by(desc(ExamAttempt.created_at))
        if exam_id:
            query = query.where(ExamAttempt.exam_id == exam_id)
        if user_id:
            query = query.where(ExamAttempt.user_id == user_id)
        if status:
            query = query.where(ExamAttempt.status == status)
        rows = (await self.db.execute(query.limit(limit))).scalars().all()
        return {
            "attempts": [
                {
                    "id": a.id, "user_id": a.user_id, "exam_id": a.exam_id, "status": a.status,
                    "total_score": a.total_score, "cefr_estimate": a.cefr_estimate,
                    "created_at": _iso(a.created_at), "submitted_at": _iso(a.submitted_at),
                }
                for a in rows
            ],
            "count": len(rows),
        }

    async def get_user_activity(
        self, inactive_days: int = 14, cefr_level: Optional[str] = None, limit: int = 20
    ) -> Dict[str, Any]:
        """Faolsiz foydalanuvchilar (oxirgi kirish N kundan oldin yoki umuman yo'q)."""
        if not self.is_admin:
            return _DENY
        cutoff = datetime.now(timezone.utc) - timedelta(days=inactive_days)
        query = (
            select(User)
            .where(User.deleted_at.is_(None), User.is_active == True,
                   or_(User.last_login_at.is_(None), User.last_login_at < cutoff))
            .order_by(User.last_login_at.asc().nullsfirst())
        )
        if cefr_level:
            query = query.where(User.cefr_level == cefr_level)
        total = await self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        rows = (await self.db.execute(query.limit(limit))).scalars().all()
        await self._audit("get_user_activity", "users", {"inactive_days": inactive_days, "returned": len(rows)})
        return {
            "inactive_days": inactive_days,
            "total_inactive": total,
            "users": [
                {"id": u.id, "full_name": u.full_name, "cefr_level": u.cefr_level,
                 "last_login_at": _iso(u.last_login_at), "created_at": _iso(u.created_at)}
                for u in rows
            ],
        }

    async def list_content(
        self, search: Optional[str] = None, content_type: Optional[str] = None, limit: int = 20
    ) -> Dict[str, Any]:
        """Kontent (video/fayl) ro'yxati."""
        if not self.is_admin:
            return _DENY
        query = select(ContentItem).order_by(desc(ContentItem.created_at))
        if search:
            query = query.where(ContentItem.title.ilike(f"%{search}%"))
        if content_type:
            query = query.where(ContentItem.content_type == content_type)
        rows = (await self.db.execute(query.limit(limit))).scalars().all()
        return {
            "items": [
                {"id": c.id, "title": c.title, "content_type": c.content_type,
                 "is_active": c.is_active, "created_at": _iso(c.created_at)}
                for c in rows
            ],
            "count": len(rows),
        }

    async def get_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """AI agent ishlatilishi: tool chaqiruvlari (audit) va exam AI job'lar holati."""
        if not self.is_admin:
            return _DENY
        since = datetime.now(timezone.utc) - timedelta(days=days)
        audit_rows = await self.db.execute(
            select(AuditLog.action, func.count(AuditLog.id))
            .where(AuditLog.action.like("ai_agent.%"), AuditLog.created_at >= since)
            .group_by(AuditLog.action)
        )
        job_rows = await self.db.execute(
            select(ExamAIJob.status, func.count(ExamAIJob.id)).where(ExamAIJob.created_at >= since).group_by(ExamAIJob.status)
        )
        return {
            "days": days,
            "ai_agent_actions": {a.replace("ai_agent.", ""): c for a, c in audit_rows.all()},
            "exam_ai_jobs_by_status": {s or "unknown": c for s, c in job_rows.all()},
        }

    # ═══════════════════════════════════════════════════════════
    # O'QISH — USER
    # ═══════════════════════════════════════════════════════════

    async def get_my_progress(self, limit: int = 10) -> Dict[str, Any]:
        """Foydalanuvchining o'z natijalari dinamikasi."""
        rows = (
            await self.db.execute(
                select(ExamAttempt)
                .where(ExamAttempt.user_id == self.current_user_id, ExamAttempt.total_score.isnot(None))
                .order_by(desc(ExamAttempt.created_at))
                .limit(limit)
            )
        ).scalars().all()
        chronological = list(reversed(rows))
        scores = [a.total_score for a in chronological]
        trend = None
        if len(scores) >= 2:
            trend = round(scores[-1] - scores[0], 2)
        return {
            "attempts": [
                {"id": a.id, "exam_id": a.exam_id, "total_score": a.total_score,
                 "cefr_estimate": a.cefr_estimate, "created_at": _iso(a.created_at)}
                for a in chronological
            ],
            "count": len(rows),
            "score_change_first_to_last": trend,
            "best_score": max(scores) if scores else None,
        }

    # ═══════════════════════════════════════════════════════════
    # YOZISH — 1-BOSQICH (prepare): tasdiqlash so'raladi
    # ═══════════════════════════════════════════════════════════

    async def _prepare(self, action: str, params: Dict[str, Any], summary: str) -> Dict[str, Any]:
        if not self.is_admin:
            return _DENY
        if self.pending_store is None:
            return {"error": "Bu amalni faqat chatda, tasdiqlash tugmasi bilan bajarish mumkin."}
        action_id = await self.pending_store.create(action, params, summary)
        await self._audit("prepare", action, {"params_keys": sorted(params)})
        return {
            "status": "pending_confirmation",
            "summary": summary,
            "note": "Amal hali bajarilmadi. Foydalanuvchiga qisqacha tushuntir: pastda 'Tasdiqlash' tugmasi chiqadi. Bajarildi deb aytma.",
            "action_id": action_id,
        }

    async def _get_target(self, user_id: int) -> Optional[User]:
        return (await self.db.execute(select(User).where(User.id == user_id, User.deleted_at.is_(None)))).scalar_one_or_none()

    async def set_user_ai_enabled(self, user_id: int, enabled: bool) -> Dict[str, Any]:
        if not self.is_admin:
            return _DENY
        user = await self._get_target(user_id)
        if not user:
            return {"error": "User topilmadi"}
        verb = "YOQISH" if enabled else "O'CHIRISH"
        return await self._prepare(
            "set_user_ai_enabled", {"user_id": user_id, "enabled": bool(enabled)},
            f"{user.full_name} (ID {user.id}) uchun AI ni {verb}",
        )

    async def change_user_role(self, user_id: int, role: str) -> Dict[str, Any]:
        if not self.is_admin:
            return _DENY
        if role not in ASSIGNABLE_ROLES:
            return {"error": f"Rol quyidagilardan biri bo'lishi kerak: {', '.join(ASSIGNABLE_ROLES)}"}
        if user_id == self.current_user_id:
            return {"error": "O'z rolingizni o'zgartira olmaysiz."}
        user = await self._get_target(user_id)
        if not user:
            return {"error": "User topilmadi"}
        if user.role in PROTECTED_ROLES:
            return {"error": "Bu foydalanuvchi rolini o'zgartirib bo'lmaydi."}
        return await self._prepare(
            "change_user_role", {"user_id": user_id, "role": role},
            f"{user.full_name} (ID {user.id}) rolini '{user.role}' → '{role}' ga o'zgartirish",
        )

    async def set_user_active(self, user_id: int, active: bool) -> Dict[str, Any]:
        if not self.is_admin:
            return _DENY
        if user_id == self.current_user_id:
            return {"error": "O'zingizni faolsizlantira olmaysiz."}
        user = await self._get_target(user_id)
        if not user:
            return {"error": "User topilmadi"}
        if user.role in PROTECTED_ROLES:
            return {"error": "Bu foydalanuvchini o'zgartirib bo'lmaydi."}
        verb = "FAOLLASHTIRISH" if active else "FAOLSIZLANTIRISH (bloklash)"
        return await self._prepare(
            "set_user_active", {"user_id": user_id, "active": bool(active)},
            f"{user.full_name} (ID {user.id}) ni {verb}",
        )

    async def reply_inbox(self, message_id: int, reply: str) -> Dict[str, Any]:
        if not self.is_admin:
            return _DENY
        reply = (reply or "").strip()
        if not reply or len(reply) > 3500:
            return {"error": "Javob matni bo'sh yoki juda uzun (max 3500)."}
        msg = (await self.db.execute(select(InboxMessage).where(InboxMessage.id == message_id))).scalar_one_or_none()
        if not msg:
            return {"error": "Inbox xabari topilmadi"}
        return await self._prepare(
            "reply_inbox", {"message_id": message_id, "reply": reply},
            f"Inbox #{message_id} ga javob yuborish:\n«{reply[:PREVIEW_CHARS]}{'…' if len(reply) > PREVIEW_CHARS else ''}»",
        )

    async def close_inbox(self, message_id: int) -> Dict[str, Any]:
        if not self.is_admin:
            return _DENY
        msg = (await self.db.execute(select(InboxMessage).where(InboxMessage.id == message_id))).scalar_one_or_none()
        if not msg:
            return {"error": "Inbox xabari topilmadi"}
        return await self._prepare("close_inbox", {"message_id": message_id}, f"Inbox #{message_id} ni yopish")

    def _broadcast_filter(self, cefr_level: Optional[str], role: Optional[str]):
        conds = [User.telegram_id.isnot(None), User.deleted_at.is_(None), User.is_active == True]
        if cefr_level:
            conds.append(User.cefr_level == cefr_level)
        if role:
            conds.append(User.role == role)
        return and_(*conds)

    async def prepare_broadcast(
        self, text: str, cefr_level: Optional[str] = None, role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Broadcast tayyorlash: yuborish faqat tasdiqdan keyin."""
        if not self.is_admin:
            return _DENY
        text = (text or "").strip()
        if not text or len(text) > BROADCAST_MAX_CHARS:
            return {"error": f"Matn bo'sh yoki juda uzun (max {BROADCAST_MAX_CHARS})."}
        count = await self.db.scalar(select(func.count(User.id)).where(self._broadcast_filter(cefr_level, role))) or 0
        if count == 0:
            return {"error": "Tanlangan filtr bo'yicha qabul qiluvchi yo'q."}
        target = ", ".join(filter(None, [f"daraja {cefr_level}" if cefr_level else None, f"rol {role}" if role else None])) or "hamma"
        return await self._prepare(
            "send_broadcast", {"text": text, "cefr_level": cefr_level, "role": role},
            f"Broadcast: {count} ta foydalanuvchiga ({target}):\n«{text[:PREVIEW_CHARS]}{'…' if len(text) > PREVIEW_CHARS else ''}»",
        )

    async def create_reminder_for_user(
        self, user_id: int, text: str, reminder_type: str, time: str, date: str = "", day_of_week: Optional[int] = None
    ) -> Dict[str, Any]:
        """Boshqa foydalanuvchi uchun (oddiy, statik) eslatma — tasdiqdan keyin."""
        if not self.is_admin:
            return _DENY
        user = await self._get_target(user_id)
        if not user:
            return {"error": "User topilmadi"}
        text = (text or "").strip()
        if not text:
            return {"error": "Eslatma matni bo'sh."}
        params = {"user_id": user_id, "text": text, "reminder_type": reminder_type, "time": time,
                  "date": date or "", "day_of_week": day_of_week}
        return await self._prepare(
            "create_reminder_for_user", params,
            f"{user.full_name} (ID {user.id}) uchun {reminder_type} eslatma, {date + ' ' if date else ''}{time}:\n«{text[:PREVIEW_CHARS]}»",
        )

    # ═══════════════════════════════════════════════════════════
    # YOZISH — 2-BOSQICH (tasdiqdan keyin bajarish)
    # ═══════════════════════════════════════════════════════════

    async def execute_pending(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tasdiqlangan amalni bajaradi. Faqat admin; hammasi AuditLog'ga yoziladi."""
        if not self.is_admin:
            return _DENY
        handler = {
            "set_user_ai_enabled": self._do_set_user_ai_enabled,
            "change_user_role": self._do_change_user_role,
            "set_user_active": self._do_set_user_active,
            "reply_inbox": self._do_reply_inbox,
            "close_inbox": self._do_close_inbox,
            "send_broadcast": self._do_send_broadcast,
            "create_reminder_for_user": self._do_create_reminder_for_user,
        }.get(action)
        if handler is None:
            return {"error": "Noma'lum amal"}
        try:
            result = await handler(params)
        except Exception:
            logger.exception(f"[PENDING] {action} bajarilmadi")
            try:
                await self.db.rollback()
            except Exception:
                pass
            return {"error": "Amal bajarilmadi."}
        await self._audit("execute", action, {k: v for k, v in params.items() if k not in ("text", "reply")})
        return result

    async def _do_set_user_ai_enabled(self, p: Dict[str, Any]) -> Dict[str, Any]:
        user = await self._get_target(int(p["user_id"]))
        if not user:
            return {"error": "User topilmadi"}
        user.ai_enabled = bool(p["enabled"])
        await self.db.commit()
        return {"status": "success", "message": f"AI {'yoqildi' if user.ai_enabled else 'o`chirildi'}: {user.full_name}"}

    async def _do_change_user_role(self, p: Dict[str, Any]) -> Dict[str, Any]:
        user = await self._get_target(int(p["user_id"]))
        if not user or user.id == self.current_user_id or user.role in PROTECTED_ROLES or p["role"] not in ASSIGNABLE_ROLES:
            return {"error": "Amalga ruxsat yo'q yoki user topilmadi"}
        user.role = p["role"]
        await self.db.commit()
        return {"status": "success", "message": f"{user.full_name} roli: {user.role}"}

    async def _do_set_user_active(self, p: Dict[str, Any]) -> Dict[str, Any]:
        user = await self._get_target(int(p["user_id"]))
        if not user or user.id == self.current_user_id or user.role in PROTECTED_ROLES:
            return {"error": "Amalga ruxsat yo'q yoki user topilmadi"}
        user.is_active = bool(p["active"])
        await self.db.commit()
        return {"status": "success", "message": f"{user.full_name}: {'faol' if user.is_active else 'faolsiz'}"}

    async def _do_reply_inbox(self, p: Dict[str, Any]) -> Dict[str, Any]:
        if self.redis is None:
            return {"error": "Redis mavjud emas"}
        msg = (await self.db.execute(select(InboxMessage).where(InboxMessage.id == int(p["message_id"])))).scalar_one_or_none()
        if not msg:
            return {"error": "Inbox xabari topilmadi"}
        target = await self.db.scalar(select(User).where(User.id == msg.user_id))
        if not target or not target.telegram_id:
            return {"error": "Qabul qiluvchi Telegram'ga ulanmagan"}
        admin = await self.db.scalar(select(User).where(User.id == self.current_user_id))

        self.db.add(InboxMessageHistory(
            inbox_message_id=msg.id, sender_id=self.current_user_id,
            message_text=p["reply"], message_type="admin_reply",
        ))
        msg.admin_reply = p["reply"]
        msg.admin_id = self.current_user_id
        msg.status = "replied"
        await self.db.commit()

        await self.redis.lpush("inbox:admin_replies", json.dumps({
            "inbox_message_id": msg.id,
            "telegram_id": target.telegram_id,
            "text": p["reply"],
            "admin_name": admin.full_name if admin else "Admin",
        }, ensure_ascii=False))
        return {"status": "success", "message": f"Inbox #{msg.id} ga javob yuborish navbatga qo'yildi"}

    async def _do_close_inbox(self, p: Dict[str, Any]) -> Dict[str, Any]:
        msg = (await self.db.execute(select(InboxMessage).where(InboxMessage.id == int(p["message_id"])))).scalar_one_or_none()
        if not msg:
            return {"error": "Inbox xabari topilmadi"}
        msg.status = "closed"
        msg.admin_id = self.current_user_id
        await self.db.commit()
        return {"status": "success", "message": f"Inbox #{msg.id} yopildi"}

    async def _do_send_broadcast(self, p: Dict[str, Any]) -> Dict[str, Any]:
        if self.redis is None:
            return {"error": "Redis mavjud emas"}
        users = (await self.db.execute(select(User).where(self._broadcast_filter(p.get("cefr_level"), p.get("role"))))).scalars().all()
        if not users:
            return {"error": "Qabul qiluvchi yo'q"}

        try:
            from app.api.broadcast import BATCH_SIZE  # type: ignore
        except Exception:
            BATCH_SIZE = 25

        broadcast_id = str(uuid.uuid4())
        progress_key = f"broadcast:{broadcast_id}:progress"
        await self.redis.hset(progress_key, mapping={
            "status": "queued", "total": str(len(users)), "sent": "0", "failed": "0",
            "created_at": datetime.utcnow().isoformat(), "admin_id": str(self.current_user_id),
            "title": "AI broadcast",
        })
        await self.redis.expire(progress_key, 86400 * 7)

        content = {"content": _html.escape(p["text"], quote=False), "message_type": "text", "media_url": None}

        def to_dict(u: User) -> Dict[str, Any]:
            parts = (u.full_name or "Foydalanuvchi").strip().split(maxsplit=1)
            return {
                "id": u.id, "telegram_id": u.telegram_id, "first_name": parts[0],
                "last_name": parts[1] if len(parts) > 1 else "", "full_name": u.full_name or "",
                "telegram_username": u.telegram_username or "", "phone": u.phone or "",
                "email": u.email or "", "cefr_level": u.cefr_level or "",
            }

        batches = 0
        for i in range(0, len(users), BATCH_SIZE):
            await self.redis.lpush("myestro:broadcast:queue", json.dumps({
                "id": broadcast_id, "batch_number": i // BATCH_SIZE + 1,
                "users": [to_dict(u) for u in users[i:i + BATCH_SIZE]],
                "content": content, "progress_key": progress_key,
            }, ensure_ascii=False))
            batches += 1
        return {"status": "success", "message": f"Broadcast navbatga qo'yildi: {len(users)} ta foydalanuvchi, {batches} paket"}

    async def _do_create_reminder_for_user(self, p: Dict[str, Any]) -> Dict[str, Any]:
        target = await self._get_target(int(p["user_id"]))
        if not target:
            return {"error": "User topilmadi"}
        sibling = type(self)(self.db, target.id, False)
        res = await sibling.create_reminder(
            text=p["text"], reminder_type=p["reminder_type"], time=p["time"],
            date=p.get("date") or "", day_of_week=p.get("day_of_week"),
        )
        if res.get("error"):
            return res
        return {"status": "success", "message": f"Eslatma yaratildi ({target.full_name}): {res.get('due_at_local')}"}


# ═══════════════════════════════════════════════════════════════
# TOOL SCHEMALARI
# ═══════════════════════════════════════════════════════════════

def _fn(name: str, description: str, properties: Dict[str, Any], required: Optional[List[str]] = None) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required or []},
        },
    }


EXTRA_ADMIN_TOOLS: List[Dict[str, Any]] = [
    _fn("get_exam_analytics",
        "Bitta exam bo'yicha analitika: urinishlar, o'rtacha ball, CEFR taqsimoti, blok turlari bo'yicha ball va eng qiyin savollar.",
        {"exam_id": {"type": "integer", "description": "Exam ID"}}, ["exam_id"]),
    _fn("list_attempts",
        "Urinishlar ro'yxati; exam_id, user_id yoki status bo'yicha filtrlash mumkin.",
        {"exam_id": {"type": "integer"}, "user_id": {"type": "integer"},
         "status": {"type": "string"}, "limit": {"type": "integer", "description": "Max 50"}}),
    _fn("get_user_activity",
        "Faolsiz foydalanuvchilar: oxirgi kirish N kundan oldin (yoki hech qachon). CEFR bo'yicha filtr mumkin.",
        {"inactive_days": {"type": "integer", "description": "Necha kundan beri kirmagan (default 14)"},
         "cefr_level": {"type": "string", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
         "limit": {"type": "integer"}}),
    _fn("list_content", "Kontent (video/fayl) ro'yxati va qidiruv.",
        {"search": {"type": "string"}, "content_type": {"type": "string", "enum": ["video", "file"]},
         "limit": {"type": "integer"}}),
    _fn("get_usage_stats", "AI agent ishlatilishi va exam AI job'lar holati oxirgi N kun uchun.",
        {"days": {"type": "integer", "description": "default 7"}}),
    # Yozish (tasdiqlash tugmasi bilan)
    _fn("set_user_ai_enabled",
        "Foydalanuvchi uchun AI ni yoqish/o'chirish. Tasdiqlash tugmasi chiqadi, darhol bajarilmaydi.",
        {"user_id": {"type": "integer"}, "enabled": {"type": "boolean"}}, ["user_id", "enabled"]),
    _fn("change_user_role",
        "Foydalanuvchi rolini o'zgartirish (student/teacher/admin). Tasdiqlash tugmasi chiqadi.",
        {"user_id": {"type": "integer"}, "role": {"type": "string", "enum": list(ASSIGNABLE_ROLES)}}, ["user_id", "role"]),
    _fn("set_user_active",
        "Foydalanuvchini faollashtirish yoki faolsizlantirish (bloklash). Tasdiqlash tugmasi chiqadi.",
        {"user_id": {"type": "integer"}, "active": {"type": "boolean"}}, ["user_id", "active"]),
    _fn("reply_inbox", "Inbox xabariga admin javobini yuborish. Tasdiqlash tugmasi chiqadi.",
        {"message_id": {"type": "integer"}, "reply": {"type": "string", "maxLength": 3500}}, ["message_id", "reply"]),
    _fn("close_inbox", "Inbox xabarini yopish. Tasdiqlash tugmasi chiqadi.",
        {"message_id": {"type": "integer"}}, ["message_id"]),
    _fn("prepare_broadcast",
        "Ommaviy xabar (broadcast) tayyorlash; qabul qiluvchilar soni ko'rsatiladi, yuborish faqat tasdiqdan keyin.",
        {"text": {"type": "string", "maxLength": 3500, "description": "Oddiy matn"},
         "cefr_level": {"type": "string", "enum": ["A1", "A2", "B1", "B2", "C1", "C2"]},
         "role": {"type": "string", "enum": list(ASSIGNABLE_ROLES)}}, ["text"]),
    _fn("create_reminder_for_user",
        "Boshqa foydalanuvchi uchun oddiy (statik) eslatma yaratish. Tasdiqlash tugmasi chiqadi.",
        {"user_id": {"type": "integer"}, "text": {"type": "string"},
         "reminder_type": {"type": "string", "enum": ["once", "daily", "weekly"]},
         "time": {"type": "string", "description": "HH:MM (Toshkent)"},
         "date": {"type": "string", "description": "YYYY-MM-DD (faqat once)"},
         "day_of_week": {"type": "integer", "description": "0-6 (faqat weekly)"}},
        ["user_id", "text", "reminder_type", "time"]),
]

EXTRA_USER_TOOLS: List[Dict[str, Any]] = [
    _fn("get_my_progress",
        "Foydalanuvchining o'z natijalari dinamikasi: oxirgi urinishlar, eng yaxshi ball, o'zgarish.",
        {"limit": {"type": "integer", "description": "Max 50, default 10"}}),
]
