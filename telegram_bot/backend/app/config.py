from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = "postgresql://myestro:myestro_password@localhost:5433/myestro"

    # Redis (DB 0 — OTP, rate limiting, cache)
    REDIS_URL: str = "redis://localhost:6380/0"

    # JWT
    JWT_ACCESS_SECRET: str = "your-access-secret-here"
    JWT_REFRESH_SECRET: str = "your-refresh-secret-here"
    JWT_ACCESS_EXPIRE: int = 15  # minutes
    JWT_REFRESH_EXPIRE: int = 10080  # minutes (7 days)

    # OpenRouter
    OPENROUTER_API_KEY: str = "sk-or-v1-your-key-here"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Telegram (for content upload to private channel)
    BOT_TOKEN: str = ""
    TELEGRAM_CONTENT_BASE: str = ""  # e.g. -1001234567890

    # Channel (for inbox subscription check)
    CHANNEL_ID: str = ""  # e.g. -1001234567890
    CHANNEL_USERNAME: str = ""  # e.g. testmyestro
    CHANNEL_URL: str = ""  # e.g. https://t.me/testmyestro

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3002,http://localhost:8002"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # Read from root .env first, fallback to empty string for Docker (env vars from docker-compose)
    model_config = {
        "env_file": (
            "../../../.env" if os.path.exists("../../../.env") else ".env"
        ),
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
