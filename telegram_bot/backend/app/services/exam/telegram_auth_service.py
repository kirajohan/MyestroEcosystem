"""
Telegram Login Widget verification va user yaratish servisi.

Telegram Login Widget hash tekshirish rasmiy algoritmi:
https://core.telegram.org/widgets/login#checking-authorization
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.exam import TelegramLoginRequest

logger = logging.getLogger(__name__)


class TelegramAuthService:
    """Telegram Login Widget orqali autentifikatsiya."""

    # Hash qancha vaqt yangi hisoblanadi (Telegram 1 kun tavsiya qiladi)
    HASH_MAX_AGE_SEC = 86400

    def verify_hash(self, data: TelegramLoginRequest) -> bool:
        """Telegram tomonidan berilgan hash ni bot token bilan tekshiradi.

        Algoritm:
        1. hash dan boshqa barcha maydonlarni "key=value" ko'rinishida,
           key bo'yicha saralab, "\n" bilan birlashtiramiz.
        2. secret_key = SHA256(bot_token)
        3. HMAC_SHA256(secret_key, data_check_string) ni hisoblaymiz.
        4. Natijani Telegram bergan hash bilan solishtiramiz.
        """
        bot_token = getattr(settings, "BOT_TOKEN", None)
        if not bot_token:
            logger.error("BOT_TOKEN is not configured")
            return False

        # 1. data_check_string ni yaratish
        data_dict = data.model_dump(exclude_none=True)
        received_hash = data_dict.pop("hash", None)
        if not received_hash:
            return False

        data_check_arr = [
            f"{key}={value}" for key, value in sorted(data_dict.items())
        ]
        data_check_string = "\n".join(data_check_arr)

        # 2. secret_key = SHA256(bot_token)
        secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()

        # 3. HMAC_SHA256
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # 4. Solishtirish (timing attack dan himoya uchun compare_digest)
        return hmac.compare_digest(computed_hash, received_hash)

    def is_hash_fresh(self, data: TelegramLoginRequest) -> bool:
        """auth_date juda eski emasligini tekshiradi."""
        now = int(datetime.now(timezone.utc).timestamp())
        age = now - data.auth_date
        return 0 <= age <= self.HASH_MAX_AGE_SEC

    async def get_or_create_user(
        self,
        db: AsyncSession,
        data: TelegramLoginRequest,
    ) -> User:
        """telegram_id bo'yicha user ni topadi, yo'q bo'lsa yaratadi.

        Eslatma: users jadvalida `full_name` va `telegram_username` bor,
        `first_name` emas. Telegram dan kelgan first_name + last_name ni
        birlashtirib `full_name` ga saqlaymiz.
        """
        result = await db.execute(
            select(User).where(User.telegram_id == data.id)
        )
        user = result.scalar_one_or_none()

        if user is not None:
            # Mavjud user — username/avatar yangilanishi mumkin
            changed = False
            if data.username and user.telegram_username != data.username:
                user.telegram_username = data.username
                changed = True
            if data.photo_url and user.avatar_url != data.photo_url:
                user.avatar_url = data.photo_url
                changed = True
            if changed:
                await db.commit()
                await db.refresh(user)
            return user

        # Yangi user yaratish
        # Yangi user yaratish
        first = (data.first_name or "").strip()
        last = (data.last_name or "").strip()
        full_name = f"{first} {last}".strip() or data.username or "Telegram User"

        user = User(
            telegram_id=data.id,
            telegram_username=data.username,
            full_name=full_name,
            avatar_url=data.photo_url,
            email=f"tg_{data.id}@myestro.local",   # ← SUN'IY EMAIL (NOT NULL uchun)
            role="student",
            auth_provider="telegram",
            is_active=True,
            is_verified=True,
            profile_completed=False,
            cefr_level="A1",
            target_level="B1",
            lang="uz",
            learning_lang="en",
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info("Created new user from Telegram login: id=%s", user.id)
        return user


# Singleton instance
telegram_auth_service = TelegramAuthService()