import hashlib
import hmac
import time
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.config import settings

class TelegramAuthService:
    """Telegram Login Widget hash validation va user boshqaruvi"""

    @staticmethod
    def verify_telegram_hash(data: dict) -> bool:
        """
        Telegram dan kelgan ma'lumotlarni HMAC-SHA256 orqali tekshiradi.
        
        Algoritm:
        1. Hash'ni ajratib olamiz
        2. Qolgan maydonlarni alfavit bo'yicha saralaymiz
        3. Har birini \n bilan birlashtiramiz: "key1=value1\nkey2=value2"
        4. Bot token'dan SHA256 olamiz (secret_key)
        5. HMAC-SHA25256(secret_key, data_check_string) = hash
        """
        received_hash = data.get("hash")
        if not received_hash:
            return False

        # Hash maydonini chiqarib tashlaymiz
        filtered = {k: v for k, v in data.items() if k != "hash"}
        
        # Alfavit bo'yicha saralaymiz va \n bilan birlashtiramiz
        sorted_items = sorted(filtered.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

        # Bot token'dan secret key olamiz
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()

        # HMAC hisoblaymiz
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        # Solishtiramiz
        if not hmac.compare_digest(computed_hash, received_hash):
            return False

        # auth_date eskirmaganligini tekshiramiz (24 soat)
        auth_date = int(data.get("auth_date", 0))
        if time.time() - auth_date > 86400:
            return False

        return True

    @staticmethod
    async def get_or_create_user(
        db: AsyncSession,
        telegram_data: dict
    ) -> User:
        """Telegram ma'lumotlaridan user topadi yoki yaratadi"""
        telegram_id = int(telegram_data["id"])
        
        # Avval mavjud user'ni qidiramiz
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Mavjud — yangilaymiz
            user.telegram_username = telegram_data.get("username")
            if telegram_data.get("photo_url"):
                user.avatar_url = telegram_data["photo_url"]
            user.last_login_at = time.time()
        else:
            # Yangi user yaratamiz
            first_name = telegram_data.get("first_name", "")
            last_name = telegram_data.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()

            user = User(
                telegram_id=telegram_id,
                telegram_username=telegram_data.get("username"),
                full_name=full_name or f"User_{telegram_id}",
                avatar_url=telegram_data.get("photo_url"),
                role="student",
                cefr_level="A1",
                target_level="B1",
                lang="uz",
                learning_lang="en",
                auth_provider="telegram",
                provider_user_id=str(telegram_id),
                is_active=True,
                is_verified=True,
                profile_completed=False,
                last_login_at=time.time(),
            )
            db.add(user)
            await db.flush()
            await db.refresh(user)

        await db.commit()
        return user