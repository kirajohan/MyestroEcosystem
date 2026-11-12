import os
from pydantic_settings import BaseSettings


def _to_async_db_url(url: str) -> str:
    """postgresql:// -> postgresql+asyncpg://. SSL param QO'SHILMAYDI!"""
    if not url:
        return url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


class Settings(BaseSettings):
    # ─── Telegram ──────────────────────────────────────────
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")
    CHANNEL_URL: str = os.getenv("CHANNEL_URL", "")
    MEDIA_UPLOAD: str = os.getenv("MEDIA_UPLOAD", "-1004443633577")
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "")

    # ─── Database & Cache ──────────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ─── Backend ───────────────────────────────────────────
    WEBAPP_URL: str = os.getenv("WEBAPP_URL", "https://a1b2c3d4.ngrok-free.app")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "https://myestroeco-backend-production.up.railway.app")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://myestro-backend:8002")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "")  # bot -> backend servis kaliti

    # ─── AI ────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    RAG_ENABLED: bool = os.getenv("RAG_ENABLED", "true").lower() == "true"
    # ─── Auth ──────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # ─── Bot Settings ──────────────────────────────────────
    BOT_GLOBAL_ENABLED: str = os.getenv("BOT_GLOBAL_ENABLED", "true")
    AI_GLOBAL_ENABLED: str = os.getenv("AI_GLOBAL_ENABLED", "true")
    AI_TRIAL_LIMIT: int = int(os.getenv("AI_TRIAL_LIMIT", "3"))
    AI_AGENT_MODEL: str = os.getenv("AI_AGENT_MODEL", "openai/gpt-4o-mini")
    AI_STREAM_MODE: str = os.getenv("AI_STREAM_MODE", "edit")  # "edit" | "draft" (sendMessageDraft)
    AI_STREAM_DRAFT_INTERVAL: float = float(os.getenv("AI_STREAM_DRAFT_INTERVAL", "0.4"))
    AI_TG_RATE: float = float(os.getenv("AI_TG_RATE", "25"))  # barcha oqimlar uchun Telegram so'rov/s
    AI_RATE_PER_MINUTE: int = int(os.getenv("AI_RATE_PER_MINUTE", "8"))
    AI_RATE_PER_DAY: int = int(os.getenv("AI_RATE_PER_DAY", "150"))
    AI_ADMIN_RATE_PER_MINUTE: int = int(os.getenv("AI_ADMIN_RATE_PER_MINUTE", "20"))
    AI_ADMIN_RATE_PER_DAY: int = int(os.getenv("AI_ADMIN_RATE_PER_DAY", "1000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ─── Properties ────────────────────────────────────────
    @property
    def admin_ids_list(self) -> list[int]:
        """Parse ADMIN_IDS string to list of integers."""
        try:
            return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]
        except (ValueError, AttributeError):
            return []

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """asyncpg uchun tayyor URL (ssl paramssiz)."""
        return _to_async_db_url(self.DATABASE_URL)

    @property
    def DB_NEEDS_SSL(self) -> bool:
        """Railway PUBLIC proxy (rlwy.net) faqat SSL bilan ishlaydi.
        Private network (.railway.internal) uchun SSL kerak emas."""
        return "rlwy.net" in self.DATABASE_URL


settings = Settings()

# Eksport qilish (import compatibility)
API_BASE_URL = settings.API_BASE_URL
BOT_TOKEN = settings.BOT_TOKEN