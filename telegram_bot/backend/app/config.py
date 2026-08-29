from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = "postgresql://myestro:[REDACTED]@localhost:5433/myestro"

    # Redis (DB 0 — OTP, rate limiting, cache)
    REDIS_URL: str = "redis://localhost:6380/0"

    # JWT
    JWT_ACCESS_SECRET: str = "b376f24c1d2bfbaacfa9ef51027b74f40cb3aa9a8497aa50dd38c52c6bff5d07"
    JWT_REFRESH_SECRET: str = "b376f24c1d2bfbaacfa9ef51027b74f40cb3aa9a8497aa50dd38c52c6bff5d07"
    JWT_ACCESS_EXPIRE: int = 15  # minutes
    JWT_REFRESH_EXPIRE: int = 10080  # minutes (7 days)
    
    # OpenRouter
    OPENROUTER_API_KEY: str = "[REDACTED]"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    MEDIA_UPLOAD: str = os.getenv("MEDIA_UPLOAD", "-1004443633577")  # Telegram channel ID for media uploads

    # Telegram (for content upload to private channel)
    BOT_TOKEN: str = "[REDACTED]"
    TELEGRAM_CONTENT_BASE: str = "-1004336645032"  # e.g. -1001234567890
    
    # Channel (for inbox subscription check)
    CHANNEL_ID: str = "-1003933846027"  # e.g. -1001234567890
    CHANNEL_USERNAME: str = "testmyestro"  # e.g. testmyestro
    CHANNEL_URL: str = "https://t.me/testmyestro"  # e.g. https://t.me/testmyestro

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3001,http://localhost:3002,http://localhost:8002,http://admin:3000,http://exam:3000,http://backend:8000"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # Read from environment first, fallback to defaults for Docker
    model_config = {
        "env_file": (
            "../../../.env" if os.path.exists("../../../.env") else ".env"
        ),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


settings = Settings()
