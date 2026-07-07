import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")
    CHANNEL_URL: str = os.getenv("CHANNEL_URL", "")  # e.g., https://t.me/testmyestro
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8002")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://myestro-backend:8002")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    AI_TRIAL_LIMIT: int = int(os.getenv("AI_TRIAL_LIMIT", "3"))
    
    # Bot Settings (Phase 2)
    BOT_GLOBAL_ENABLED: str = os.getenv("BOT_GLOBAL_ENABLED", "true")
    AI_GLOBAL_ENABLED: str = os.getenv("AI_GLOBAL_ENABLED", "true")
    ADMIN_IDS: str = os.getenv("ADMIN_IDS", "123456789")  # Comma-separated
    
    @property
    def admin_ids_list(self) -> list[int]:
        """Parse ADMIN_IDS string to list of integers."""
        try:
            return [int(id.strip()) for id in self.ADMIN_IDS.split(",")]
        except (ValueError, AttributeError):
            return []

settings = Settings()

# 📤 Eksport qilish (shu bilan import ishlaydi)
API_BASE_URL = settings.API_BASE_URL
BOT_TOKEN = settings.BOT_TOKEN
