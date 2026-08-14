"""
bot/services/broadcast_worker.py

Redis navbatidan (myestro:broadcast:queue) broadcast job'larini o'qiydi va
foydalanuvchilarga xabar/media yuboradi. Har bir batch tugagach progress
hash'ni (broadcast:{id}:progress) yangilaydi.

MUHIM: Bu — yagona consumer bo'lishi kerak. Boshqa hech qanday joyda
(masalan eski bot/handlers/broadcast.py) shu queue'ni o'qimang.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
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

# Telegram'ning oddiy xabar limiti taxminan 30 msg/sek (bulk uchun ~25-30 xavfsizroq).
# Shu bilan birga bitta chatga tez-tez yozish ham cheklangan — shuning uchun har bir
# yuborishdan keyin kichik sleep qo'yamiz.
SEND_INTERVAL_SECONDS = 0.04  # ~25 xabar/soniya

# BRPOP timeout (soniyalarda) — 0 bo'lsa cheksiz kutadi, lekin biz worker'ni
# tozalik bilan to'xtata olishimiz uchun kichik timeout bilan loop qilamiz.
BRPOP_TIMEOUT_SECONDS = 5


class BroadcastWorker:
    """Redis navbatini doimiy tinglab, broadcast job'larini bajaruvchi worker."""

    def __init__(self, bot: Bot, redis: Redis, queue_name: str = QUEUE_NAME) -> None:
        self.bot = bot
        self.redis = redis
        self.queue_name = queue_name
        self._running = False
        # media_url -> file_id keshi (bitta process davomida qayta yuklamaslik uchun)
        self._media_cache: dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Asosiy loop
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        """Worker loop'ni ishga tushiradi. main.py'da asyncio.create_task bilan chaqiriladi."""
        self._running = True
        logger.info("🎧 Broadcast worker started, listening on '%s'...", self.queue_name)

        while self._running:
            try:
                # BRPOP: ro'yxatning o'ng tomonidan oladi (Next.js LPUSH bilan qo'shadi => FIFO)
                result = await self.redis.brpop(self.queue_name, timeout=BRPOP_TIMEOUT_SECONDS)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Redis BRPOP xatosi, 2 soniyadan keyin qayta urinamiz")
                await asyncio.sleep(2)
                continue

            if result is None:
                # timeout — navbatda job yo'q, loop davom etadi
                continue

            _key, raw_job = result
            try:
                job = json.loads(raw_job)
            except json.JSONDecodeError:
                logger.error("Noto'g'ri JSON formatdagi job qabul qilindi, tashlab yuborildi: %r", raw_job[:200])
                continue

            try:
                await self._process_job(job)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Job'ni qayta ishlashda kutilmagan xato: %r", job.get("id"))

        logger.info("Broadcast worker to'xtatildi.")

    async def stop(self) -> None:
        """Loop'ni tozalik bilan to'xtatadi. main.py'ning finally blokida chaqiriladi."""
        self._running = False

    # ------------------------------------------------------------------ #
    # Job'ni qayta ishlash
    # ------------------------------------------------------------------ #

    async def _process_job(self, job: dict[str, Any]) -> None:
        broadcast_id = job.get("id")
        batch_number = job.get("batch_number")
        user_ids: list[int] = job.get("user_ids", [])
        content: dict[str, Any] = job.get("content", {})
        progress_key: str | None = job.get("progress_key")

        if not progress_key:
            # Producer bilan schema mos kelmayapti — progress_key bo'lmasa hisoblay olmaymiz
            logger.error("Job'da progress_key yo'q (broadcast_id=%s, batch=%s)", broadcast_id, batch_number)
            return

        logger.info(
            "Batch #%s qayta ishlanmoqda: broadcast_id=%s, %d ta foydalanuvchi",
            batch_number, broadcast_id, len(user_ids),
        )

        # Birinchi job kelganda statusni pending -> sending ga o'tkazamiz
        await self.redis.hset(progress_key, "status", "sending")

        for user_id in user_ids:
            success = await self._send_message(user_id, content)

            field = "sent" if success else "failed"
            await self.redis.hincrby(progress_key, field, 1)

            # Telegram rate limitini buzmaslik uchun
            await asyncio.sleep(SEND_INTERVAL_SECONDS)

        # Batch tugadi — agar bu oxirgi batch bo'lsa (barcha sent+failed == total),
        # umumiy statusni "completed" ga o'tkazamiz.
        total = int(await self.redis.hget(progress_key, "total") or 0)
        sent = int(await self.redis.hget(progress_key, "sent") or 0)
        failed = int(await self.redis.hget(progress_key, "failed") or 0)
        if total and (sent + failed) >= total:
            await self.redis.hset(progress_key, "status", "completed")
            logger.info(
                "Broadcast tugadi: id=%s, jami=%d, yuborildi=%d, xato=%d",
                broadcast_id, total, sent, failed,
            )

    # ------------------------------------------------------------------ #
    # Bitta foydalanuvchiga xabar/media yuborish
    # ------------------------------------------------------------------ #

    async def _send_message(self, user_id: int, content: dict[str, Any]) -> bool:
        """
        content sxemasi (Next.js producer bilan kelishilgan):
        {
            "content": "<b>Xabar matni</b>",   # yoki "text"
            "message_type": "text" | "photo" | "video" | "document",  # yoki "media_type"
            "media_url": "https://..." | null
        }
        Kamida bitta variant (content/text, message_type/media_type) mavjud bo'lishi kerak.
        """
        text = content.get("content") or content.get("text") or ""
        message_type = content.get("message_type") or content.get("media_type") or "text"
        media_url = content.get("media_url")

        try:
            if message_type == "text" or not media_url:
                await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
                return True

            # Keshda file_id bo'lsa o'shani, bo'lmasa to'g'ridan-to'g'ri public URL'ni ishlatamiz.
            cache_key = hashlib.sha256(media_url.encode()).hexdigest()
            media_source = self._media_cache.get(cache_key, media_url)

            if message_type == "photo":
                msg = await self.bot.send_photo(chat_id=user_id, photo=media_source, caption=text, parse_mode="HTML")
                if cache_key not in self._media_cache and msg.photo:
                    self._media_cache[cache_key] = msg.photo[-1].file_id
            elif message_type == "video":
                msg = await self.bot.send_video(chat_id=user_id, video=media_source, caption=text, parse_mode="HTML")
                if cache_key not in self._media_cache and msg.video:
                    self._media_cache[cache_key] = msg.video.file_id
            elif message_type == "document":
                msg = await self.bot.send_document(chat_id=user_id, document=media_source, caption=text, parse_mode="HTML")
                if cache_key not in self._media_cache and msg.document:
                    self._media_cache[cache_key] = msg.document.file_id
            else:
                logger.warning("Noma'lum message_type: %s, matn sifatida yuborildi", message_type)
                await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
            return True

        except TelegramForbiddenError:
            # Foydalanuvchi botni bloklagan yoki chatni o'chirgan — xato emas, kutilgan holat
            logger.debug("Foydalanuvchi %s botni bloklagan, o'tkazib yuborildi", user_id)
            return False

        except TelegramRetryAfter as e:
            # Telegram flood control ishga tushdi — kutib, bitta marta qayta urinib ko'ramiz
            logger.warning("FloodWait: %s soniya kutamiz (user_id=%s)", e.retry_after, user_id)
            await asyncio.sleep(e.retry_after + 0.5)
            try:
                return await self._send_message(user_id, content)
            except Exception:
                logger.exception("Qayta urinishdan keyin ham xato (user_id=%s)", user_id)
                return False

        except (TelegramBadRequest, TelegramNotFound) as e:
            logger.warning("Yuborib bo'lmadi (user_id=%s): %s", user_id, e)
            return False

        except Exception:
            logger.exception("Kutilmagan xato (user_id=%s)", user_id)
            return False