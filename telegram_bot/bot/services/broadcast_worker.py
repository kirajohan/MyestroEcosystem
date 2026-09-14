"""
bot/services/broadcast_worker.py

Redis queue'dan broadcast job'larni o'qib, har bir foydalanuvchiga
shaxsiylashtirilgan xabar yuboradi. Har bir job'da user ma'lumotlari
oldindan qoshilgan boladi (producer tomonidan).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from typing import Any

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
    TelegramRetryAfter,
)
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

QUEUE_NAME = "myestro:broadcast:queue"
SEND_INTERVAL_SECONDS = 0.04
BRPOP_TIMEOUT_SECONDS = 5

# Regex placeholder'larni tez topish uchun
PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")


class BroadcastWorker:
    """Redis queue'ni tinglab, broadcast job'larni bajaruvchi worker."""

    def __init__(self, bot: Bot, redis: Redis, queue_name: str = QUEUE_NAME) -> None:
        self.bot = bot
        self.redis = redis
        self.queue_name = queue_name
        self._running = False
        self._media_cache: dict[str, str] = {}

    async def start(self) -> None:
        self._running = True
        logger.info("🎧 Broadcast worker started, listening on '%s'...", self.queue_name)

        while self._running:
            try:
                result = await self.redis.brpop(self.queue_name, timeout=BRPOP_TIMEOUT_SECONDS)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Redis BRPOP xatosi, 2 soniyadan keyin qayta urinamiz")
                await asyncio.sleep(2)
                continue

            if result is None:
                continue

            _key, raw_job = result
            try:
                job = json.loads(raw_job)
            except json.JSONDecodeError:
                logger.error("Noto'g'ri JSON: %r", raw_job[:200])
                continue

            try:
                await self._process_job(job)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Job xatosi: %r", job.get("id"))

        logger.info("Broadcast worker to'xtatildi.")

    async def stop(self) -> None:
        self._running = False

    async def _process_job(self, job: dict[str, Any]) -> None:
        broadcast_id = job.get("id")
        batch_number = job.get("batch_number")
        users: list[dict[str, Any]] = job.get("users", [])
        content: dict[str, Any] = job.get("content", {})
        progress_key: str | None = job.get("progress_key")

        if not progress_key:
            logger.error("progress_key yo'q (broadcast_id=%s)", broadcast_id)
            return

        # Legacy support — eski schema (faqat user_ids)
        if not users and "user_ids" in job:
            logger.warning(
                "Eski schema: user_ids berilgan, lekin user ma'lumotlari yo'q. "
                "Shaxsiylashtirish ishlamaydi. (broadcast_id=%s)",
                broadcast_id,
            )
            users = [{"telegram_id": uid} for uid in job.get("user_ids", [])]

        logger.info(
            "Batch #%s: broadcast_id=%s, %d ta foydalanuvchi",
            batch_number, broadcast_id, len(users),
        )

        await self.redis.hset(progress_key, "status", "sending")

        for user in users:
            telegram_id = user.get("telegram_id")
            if not telegram_id:
                await self.redis.hincrby(progress_key, "failed", 1)
                continue

            success = await self._send_to_user(telegram_id, content, user)
            field = "sent" if success else "failed"
            await self.redis.hincrby(progress_key, field, 1)
            await asyncio.sleep(SEND_INTERVAL_SECONDS)

        total = int(await self.redis.hget(progress_key, "total") or 0)
        sent = int(await self.redis.hget(progress_key, "sent") or 0)
        failed = int(await self.redis.hget(progress_key, "failed") or 0)
        if total and (sent + failed) >= total:
            await self.redis.hset(progress_key, "status", "completed")
            logger.info(
                "Broadcast tugadi: id=%s, total=%d, sent=%d, failed=%d",
                broadcast_id, total, sent, failed,
            )

    # ------------------------------------------------------------------ #
    # Shaxsiylashtirish
    # ------------------------------------------------------------------ #

    @staticmethod
    def render_template(content: str, user: dict[str, Any]) -> str:
        """
        Xabar matnidagi {placeholder}'larni user ma'lumotlari bilan almashtiradi.
        
        Qollab-quvvatlanadigan placeholder'lar:
          {first_name}, {last_name}, {full_name}, {username},
          {phone}, {email}, {cefr_level}, {telegram_id}, {user_id}
        """
        if not content:
            return content

        # Fallback qiymatlar
        first_name = user.get("first_name") or user.get("full_name") or "Foydalanuvchi"
        last_name = user.get("last_name") or ""
        full_name = user.get("full_name") or f"{first_name} {last_name}".strip() or first_name
        username_raw = user.get("telegram_username") or user.get("username") or ""
        username = f"@{username_raw}" if username_raw else ""
        phone = user.get("phone") or ""
        email = user.get("email") or ""
        cefr_level = user.get("cefr_level") or ""
        telegram_id = str(user.get("telegram_id") or "")
        user_id = str(user.get("id") or "")

        replacements = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "username": username,
            "phone": phone,
            "email": email,
            "cefr_level": cefr_level,
            "telegram_id": telegram_id,
            "user_id": user_id,
        }

        def replace_match(match: re.Match) -> str:
            key = match.group(1)
            return replacements.get(key, match.group(0))  # topilmasa o'zini qoldiradi

        return PLACEHOLDER_RE.sub(replace_match, content)

    # ------------------------------------------------------------------ #
    # Bitta userga yuborish
    # ------------------------------------------------------------------ #

    async def _send_to_user(
        self, user_id: int, content: dict[str, Any], user: dict[str, Any]
    ) -> bool:
        raw_text = content.get("content") or content.get("text") or ""
        message_type = content.get("message_type") or content.get("media_type") or "text"
        media_url = content.get("media_url")

        # Shaxsiylashtirish
        text = self.render_template(raw_text, user)

        try:
            if message_type == "text" or not media_url:
                await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
                return True

            cache_key = hashlib.sha256(media_url.encode()).hexdigest()
            media_source = self._media_cache.get(cache_key, media_url)

            if message_type == "photo":
                msg = await self.bot.send_photo(
                    chat_id=user_id, photo=media_source, caption=text, parse_mode="HTML"
                )
                if cache_key not in self._media_cache and msg.photo:
                    self._media_cache[cache_key] = msg.photo[-1].file_id
            elif message_type == "video":
                msg = await self.bot.send_video(
                    chat_id=user_id, video=media_source, caption=text, parse_mode="HTML"
                )
                if cache_key not in self._media_cache and msg.video:
                    self._media_cache[cache_key] = msg.video.file_id
            elif message_type == "document":
                msg = await self.bot.send_document(
                    chat_id=user_id, document=media_source, caption=text, parse_mode="HTML"
                )
                if cache_key not in self._media_cache and msg.document:
                    self._media_cache[cache_key] = msg.document.file_id
            else:
                await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
            return True

        except TelegramForbiddenError:
            logger.debug("User %s botni bloklagan", user_id)
            return False

        except TelegramRetryAfter as e:
            logger.warning("FloodWait: %s soniya (user_id=%s)", e.retry_after, user_id)
            await asyncio.sleep(e.retry_after + 0.5)
            try:
                return await self._send_to_user(user_id, content, user)
            except Exception:
                logger.exception("Retry xatosi (user_id=%s)", user_id)
                return False

        except (TelegramBadRequest, TelegramNotFound) as e:
            logger.warning("Yuborib bo'lmadi (user_id=%s): %s", user_id, e)
            return False

        except Exception:
            logger.exception("Kutilmagan xato (user_id=%s)", user_id)
            return False