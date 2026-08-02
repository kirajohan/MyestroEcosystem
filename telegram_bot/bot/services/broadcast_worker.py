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
import html
import json
import logging
from typing import Any, Optional

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramNotFound,
    TelegramRetryAfter,
)
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument
from redis.asyncio import Redis

from bot.config import settings

logger = logging.getLogger(__name__)

QUEUE_NAME = "myestro:broadcast:queue"

# Telegram'ning oddiy xabar limiti taxminan 30 msg/sek (bulk uchun ~25-30 xavfsizroq).
# Shu bilan birga bitta chatga tez-tez yozish ham cheklangan — shuning uchun har bir
# yuborishdan keyin kichik sleep qo'yamiz.
SEND_INTERVAL_SECONDS = 0.04  # ~25 xabar/soniya

# BRPOP timeout (soniyalarda) — 0 bo'lsa cheksiz kutadi, lekin biz worker'ni
# tozalik bilan to'xtata olishimiz uchun kichik timeout bilan loop qilamiz.
BRPOP_TIMEOUT_SECONDS = 5

# Archive channel — used for sending broadcast copies and media uploads
# Priority: ARCHIVE_CHAT_ID → TELEGRAM_CONTENT_BASE
ARCHIVE_CHAT_ID = getattr(settings, "ARCHIVE_CHAT_ID", None) or getattr(settings, "TELEGRAM_CONTENT_BASE", None)

# Import placeholder registry (fetched from backend via HTTP)
from bot.services.placeholder_registry import (
    PLACEHOLDER_REGISTRY,
    get_placeholders_from_backend,
)


def render_template(content: str, user: dict) -> str:
    """Replace placeholders with actual user data.
    
    PLACEHOLDER_REGISTRY is a dict mapping placeholder keys to their values.
    Example: {"{full_name}": "{full_name}", "{email}": "{email}"}
    """
    if not content:
        return content
    
    replacements = {}
    for key in PLACEHOLDER_REGISTRY:
        # key is like "{full_name}"
        field_name = key.strip("{}")
        value = user.get(field_name)
        
        # Handle None/empty values with fallbacks
        if value is None:
            if field_name in ["is_active", "is_verified", "profile_completed", "ai_enabled"]:
                value = "false"
            elif field_name == "lang":
                value = "uz"
            elif field_name == "learning_lang":
                value = "en"
            elif field_name == "role":
                value = "student"
            elif field_name in ["cefr_level", "target_level"]:
                value = "A1"
            else:
                value = "-"
        else:
            # Convert booleans to strings
            if isinstance(value, bool):
                value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                value = str(value)
        
        # Escape HTML for safety
        replacements[key] = html.escape(str(value))
    
    for key, value in replacements.items():
        content = content.replace(key, value)
    return content


class BroadcastWorker:
    """Redis navbatini doimiy tinglab, broadcast job'larini bajaruvchi worker."""

    def __init__(self, bot: Bot, redis: Redis, queue_name: str = QUEUE_NAME) -> None:
        self.bot = bot
        self.redis = redis
        self.queue_name = queue_name
        self._running = False
        # media_url -> file_id keshi (bitta process davomida qayta yuklamaslik uchun)
        self._media_cache: dict[str, str] = {}
        # user_id -> user_data kesh (placeholder rendering uchun)
        self._user_cache: dict[int, dict] = {}
        # Redis decode_responses=False uchun alohida ulanish (binary ma'lumotlar)
        self._redis_binary: Optional[Redis] = None

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
        # Check for media upload jobs
        if job.get("type") == "media_upload":
            await self._handle_media_upload(job)
            return
        
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
            "📊 Batch #%s qayta ishlanmoqda: broadcast_id=%s, %d ta foydalanuvchi, progress_key=%s",
            batch_number, broadcast_id, len(user_ids), progress_key,
        )
        logger.info("📊 Content: %s", json.dumps(content, ensure_ascii=False)[:200])

        # ✅ Birinchi job kelganda statusni pending -> sending ga o'tkazamiz
        await self.redis.hset(progress_key, "status", "sending")
        logger.info("✅ Status updated to 'sending' for broadcast_id=%s", broadcast_id)
        
        # ✅ Fetch fresh placeholders from backend (cached)
        try:
            fresh_placeholders = await get_placeholders_from_backend()
            if fresh_placeholders:
                # Update the global PLACEHOLDER_REGISTRY for this job
                global PLACEHOLDER_REGISTRY
                PLACEHOLDER_REGISTRY = fresh_placeholders
                logger.info("✅ Updated placeholder registry with %d placeholders", len(fresh_placeholders))
                logger.info("📊 Placeholder keys: %s", list(fresh_placeholders.keys())[:5])
        except Exception as e:
            logger.warning("⚠️ Could not fetch fresh placeholders, using cached: %s", e)

        try:
            # === PHASE 4: Archive channel ===
            # Send to archive channel first, then to users
            archive_message_id = None
            if ARCHIVE_CHAT_ID:
                try:
                    # Use the first user as sample for archive (no placeholders)
                    archive_msg = await self._send_to_archive(content)
                    if archive_msg:
                        archive_message_id = archive_msg.message_id
                        await self.redis.hset(progress_key, "archive_message_id", str(archive_message_id))
                        logger.info("✅ Archive message sent: id=%s, msg_id=%s", broadcast_id, archive_message_id)
                except Exception as e:
                    logger.error("❌ Archive channel error (id=%s): %s", broadcast_id, e)

            # === PHASE 5: Send to users with placeholder rendering ===
            user_data_map: dict[int, dict] = {}
            has_placeholders = any(p in content.get("content", "") for p in ["{", "}"])
            logger.info("📊 Has placeholders: %s", has_placeholders)
            if has_placeholders:
                logger.info("📊 Content with placeholders: %s", content.get("content", "")[:100])

            sent_count = 0
            failed_count = 0
            
            for user_id in user_ids:
                # Get user data for placeholder rendering
                if has_placeholders:
                    user_dict = await self._get_user_data(user_id)
                    logger.debug("📊 User %s data: %s", user_id, user_dict)
                else:
                    user_dict = {}
                
                personalized_content = content.copy()
                if has_placeholders and user_dict:
                    personalized_content["content"] = render_template(content.get("content", ""), user_dict)
                    personalized_content["text"] = render_template(content.get("text", ""), user_dict)
                    logger.debug("📧 Rendered content for user %s: %s", user_id, personalized_content["content"][:100])
                
                success = await self._send_message(user_id, personalized_content)

                field = "sent" if success else "failed"
                await self.redis.hincrby(progress_key, field, 1)
                
                if success:
                    sent_count += 1
                    logger.debug("✅ Sent to user %s (total sent: %d)", user_id, sent_count)
                else:
                    failed_count += 1
                    logger.debug("❌ Failed for user %s (total failed: %d)", user_id, failed_count)

                # Telegram rate limitini buzmaslik uchun
                await asyncio.sleep(SEND_INTERVAL_SECONDS)

            logger.info(
                "📊 Batch completed: broadcast_id=%s, sent=%d, failed=%d",
                broadcast_id, sent_count, failed_count,
            )

        except Exception as e:
            logger.exception("❌ Broadcast job processing error (id=%s): %s", broadcast_id, e)
            await self.redis.hincrby(progress_key, "error_count", 1)
        
        finally:
            # Batch tugadi — agar bu oxirgi batch bo'lsa (barcha sent+failed == total),
            # umumiy statusni "completed" yoki "failed" ga o'tkazamiz.
            total = int(await self.redis.hget(progress_key, "total") or 0)
            sent = int(await self.redis.hget(progress_key, "sent") or 0)
            failed = int(await self.redis.hget(progress_key, "failed") or 0)
            error_count = int(await self.redis.hget(progress_key, "error_count") or 0)
            
            if total and (sent + failed) >= total:
                # All users processed - mark as completed
                await self.redis.hset(progress_key, "status", "completed")
                logger.info(
                    "Broadcast tugadi: id=%s, jami=%d, yuborildi=%d, xato=%d",
                    broadcast_id, total, sent, failed,
                )
            elif error_count > 0 and (sent + failed + error_count) >= total:
                # All processed with errors - mark as completed (partial success)
                await self.redis.hset(progress_key, "status", "completed")
                logger.info(
                    "Broadcast completed with errors: id=%s, jami=%d, yuborildi=%d, xato=%d, xatolar=%d",
                    broadcast_id, total, sent, failed, error_count,
                )

    # ------------------------------------------------------------------ #
    # PHASE 3: Media upload handler
    # ------------------------------------------------------------------ #

    async def _handle_media_upload(self, job: dict[str, Any]) -> None:
        """Handle media upload job — send file from Redis to Telegram storage channel."""
        file_id = job.get("file_id")
        filename = job.get("filename", "unnamed")
        content_type = job.get("content_type", "application/octet-stream")

        if not file_id:
            logger.error("Media upload job has no file_id")
            return

        if not ARCHIVE_CHAT_ID:
            logger.error("Cannot upload media: ARCHIVE_CHAT_ID not configured")
            await self.redis.hset(f"upload:{file_id}", "status", "error:no_archive_channel")
            return

        logger.info("Processing media upload: file_id=%s, filename=%s", file_id, filename)

        try:
            # Get binary Redis connection
            if self._redis_binary is None:
                self._redis_binary = Redis.from_url(settings.REDIS_URL, decode_responses=False)
            
            # Read file bytes from Redis
            file_bytes = await self._redis_binary.get(f"upload:{file_id}:data")
            if not file_bytes:
                logger.error("File data not found in Redis: upload:%s:data", file_id)
                await self.redis.hset(f"upload:{file_id}", "status", "error:data_not_found")
                return

            # Determine InputFile type
            from aiogram.types import BufferedInputFile
            file_input = BufferedInputFile(file_bytes, filename=filename)

            # Send to archive channel based on content type
            if content_type.startswith("image/"):
                msg = await self.bot.send_photo(chat_id=ARCHIVE_CHAT_ID, photo=file_input)
                telegram_file_id = msg.photo[-1].file_id
            elif content_type.startswith("video/"):
                msg = await self.bot.send_video(chat_id=ARCHIVE_CHAT_ID, video=file_input)
                telegram_file_id = msg.video.file_id
            else:
                msg = await self.bot.send_document(chat_id=ARCHIVE_CHAT_ID, document=file_input)
                telegram_file_id = msg.document.file_id

            # Update Redis with the Telegram file_id
            await self.redis.hset(f"upload:{file_id}", mapping={
                "telegram_file_id": telegram_file_id,
                "status": "completed",
            })
            logger.info("Media upload completed: file_id=%s, telegram_file_id=%s", file_id, telegram_file_id)

        except Exception as e:
            logger.exception("Media upload failed: file_id=%s", file_id)
            await self.redis.hset(f"upload:{file_id}", "status", f"error:{str(e)}")

    # ------------------------------------------------------------------ #
    # PHASE 4: Send to archive channel
    # ------------------------------------------------------------------ #

    async def _send_to_archive(self, content: dict[str, Any]) -> Any:
        """Send a copy of broadcast content to the archive channel."""
        if not ARCHIVE_CHAT_ID:
            return None

        text = content.get("content") or content.get("text") or ""
        message_type = content.get("message_type") or content.get("media_type") or "text"
        media_url = content.get("media_url")

        archive_text = (
            "📢 *Broadcast Archive*\n\n"
            f"{text}\n\n"
            f"─ Yuborilgan: {text[:50]}..."
        )

        try:
            if message_type == "text" or not media_url:
                return await self.bot.send_message(chat_id=ARCHIVE_CHAT_ID, text=text, parse_mode="HTML")
            
            if message_type == "photo":
                return await self.bot.send_photo(chat_id=ARCHIVE_CHAT_ID, photo=media_url, caption=text, parse_mode="HTML")
            elif message_type == "video":
                return await self.bot.send_video(chat_id=ARCHIVE_CHAT_ID, video=media_url, caption=text, parse_mode="HTML")
            elif message_type == "document":
                return await self.bot.send_document(chat_id=ARCHIVE_CHAT_ID, document=media_url, caption=text, parse_mode="HTML")
            else:
                return await self.bot.send_message(chat_id=ARCHIVE_CHAT_ID, text=text, parse_mode="HTML")
        except Exception as e:
            logger.error("Archive send error: %s", e)
            return None

    # ------------------------------------------------------------------ #
    # PHASE 5: Get user data for placeholder rendering
    # ------------------------------------------------------------------ #

    def _sanitize_user_data(self, user_data: dict) -> dict:
        """Remove sensitive fields from user data."""
        sensitive_fields = {"password_hash", "deleted_at"}
        return {k: v for k, v in user_data.items() if k not in sensitive_fields}

    async def _get_user_data(self, user_id: int) -> dict:
        """Get user data for placeholder rendering. Uses Redis cache."""
        if user_id in self._user_cache:
            return self._user_cache[user_id]

        try:
            # Try to get user data from a dedicated Redis hash (populated by backend)
            # Note: decode_responses=True means data is already strings
            user_data = await self.redis.hgetall(f"user:{user_id}:data")
            if user_data:
                # Data is already strings (decode_responses=True)
                # Just sanitize to remove sensitive fields
                sanitized = self._sanitize_user_data(user_data)
                self._user_cache[user_id] = sanitized
                logger.info("✅ User %s data loaded from Redis: full_name=%s, email=%s", 
                           user_id, sanitized.get("full_name", "-"), sanitized.get("email", "-"))
                return sanitized
            else:
                logger.warning("⚠️ User %s data NOT found in Redis (user:%s:data is empty)", user_id, user_id)
        except Exception as e:
            logger.debug("Could not fetch user data for %s: %s", user_id, e)

        # Fallback: return minimal data with all placeholder fields
        fallback = {
            "id": str(user_id),
            "email": "-",
            "full_name": f"User {user_id}",
            "role": "student",
            "cefr_level": "A1",
            "target_level": "B1",
            "avatar_url": None,
            "phone": None,
            "lang": "uz",
            "learning_lang": "en",
            "telegram_id": str(user_id),
            "telegram_username": None,
            "auth_provider": "email",
            "provider_user_id": None,
            "is_active": "true",
            "is_verified": "false",
            "profile_completed": "false",
            "last_login_at": None,
            "location": None,
            "ai_enabled": "true",
            "created_at": None,
            "updated_at": None,
        }
        self._user_cache[user_id] = fallback
        logger.warning("⚠️ Using fallback data for user %s (Redis'da ma'lumot yo'q)", user_id)
        return fallback

    # ------------------------------------------------------------------ #
    # Bitta foydalanuvchiga xabar/media yuborish
    # ------------------------------------------------------------------ #

    def _validate_file_id(self, file_id: str) -> bool:
        """Validate Telegram file_id format.
        
        Args:
            file_id: Telegram file_id to validate
            
        Returns:
            True if file_id appears valid, False otherwise
        """
        if not file_id or not isinstance(file_id, str):
            return False
        
        # Telegram file_ids are typically base64-like strings
        # They should be at least 20 characters and contain only valid characters
        if len(file_id) < 20:
            return False
        
        # Check for common invalid patterns
        invalid_patterns = ["null", "undefined", "none", "error", "failed"]
        if file_id.lower() in invalid_patterns:
            return False
        
        # Reject UUID format (common bug: UUID used instead of Telegram file_id)
        import re
        if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', file_id, re.IGNORECASE):
            logger.warning("file_id appears to be a UUID, not a Telegram file_id: %s", file_id)
            return False
        
        # Valid file_ids typically contain alphanumeric chars, dots, underscores, hyphens
        if not re.match(r'^[A-Za-z0-9._-]+$', file_id):
            return False
        
        return True

    async def _send_message(self, user_id: int, content: dict[str, Any]) -> bool:
        """
        content sxemasi (Next.js producer bilan kelishilgan):
        {
            "content": "<b>Xabar matni</b>",   # yoki "text"
            "message_type": "text" | "photo" | "video" | "document",  # yoki "media_type"
            "media_url": "https://..." | null,
            "file_id": "telegram_file_id" | null
        }
        Kamida bitta variant (content/text, message_type/media_type) mavjud bo'lishi kerak.
        """
        text = content.get("content") or content.get("text") or ""
        message_type = content.get("message_type") or content.get("media_type") or "text"
        media_url = content.get("media_url")
        file_id = content.get("file_id")

        try:
            if message_type == "text" or not media_url:
                await self.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
                return True

            # Prioritize file_id if available and valid
            media_source = None
            if file_id and self._validate_file_id(file_id):
                media_source = file_id
            else:
                # Fallback to cached file_id or public URL
                cache_key = hashlib.sha256(media_url.encode()).hexdigest()
                media_source = self._media_cache.get(cache_key, media_url)
                
                # If using public URL, validate it's not an invalid file_id
                if media_source == file_id and not self._validate_file_id(media_source):
                    logger.warning("Invalid file_id detected, falling back to URL: %s", file_id)
                    media_source = media_url

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
