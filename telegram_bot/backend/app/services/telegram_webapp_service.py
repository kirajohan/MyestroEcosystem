"""
Telegram Mini App initData validatsiyasi.
https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
"""
import hmac
import hashlib
import json
import time
from urllib.parse import parse_qsl
from typing import Optional

from app.config import settings


class TelegramWebAppService:
    """Mini App initData'ni tekshirish."""

    @staticmethod
    def validate_init_data(init_data: str) -> Optional[dict]:
        """
        initData'ni HMAC-SHA256 orqali tekshiradi.
        
        Returns:
            user dict yoki None (agar yaroqsiz bo'lsa)
        """
        try:
            # 1. Query string'ni parse qilish
            data = dict(parse_qsl(init_data))
            received_hash = data.pop("hash", None)

            if not received_hash:
                return None

            # 2. Data check string yaratish (alfavit bo'yicha)
            data_check_string = "\n".join(
                f"{k}={v}" for k, v in sorted(data.items())
            )

            # 3. Secret key: HMAC_SHA256(bot_token, "WebAppData")
            secret_key = hmac.new(
                b"WebAppData",
                settings.TELEGRAM_BOT_TOKEN.encode(),
                hashlib.sha256,
            ).digest()

            # 4. HMAC hisoblash
            computed_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256,
            ).hexdigest()

            # 5. Solishtirish (timing attack himoyasi)
            if not hmac.compare_digest(computed_hash, received_hash):
                return None

            # 6. auth_date tekshirish (24 soat)
            auth_date = int(data.get("auth_date", 0))
            if time.time() - auth_date > 86400:
                return None

            # 7. user JSON parse
            user_json = data.get("user", "{}")
            user = json.loads(user_json)

            return user

        except Exception as e:
            print(f"initData validation xatosi: {e}")
            return None