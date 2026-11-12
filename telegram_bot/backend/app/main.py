import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Fayl boshida, boshqa import'lar yonida:
from app.websocket.admin_ws import router as websocket_router
from app.database import close_redis, SessionLocal
from app.core.exceptions import AppException
from app.api import bot_text
from app.services.cleanup_service import run_full_cleanup
from app.services.ai_service import shutdown_ai_client

# Add telegram_bot root to path so shared module is importable
_telegram_bot_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _telegram_bot_root not in sys.path:
    sys.path.insert(0, _telegram_bot_root)

from app.api import tests_import
from app.config import settings
from app.api import (
    auth, users, content, broadcast, inbox, settings as settings_router,
    stats, knowledge, ai_assistant, admin, sync, admin_messages, logs, tests
)
from app.websocket.admin_ws import router as ws_router
from app.services.admin_ai_service import AIToolsService
from app.services.ai_agent import AIAgent

from app.api.exam_v2.router import exam_v2_router

logger = logging.getLogger(__name__)

# Scheduler
scheduler = AsyncIOScheduler(timezone="UTC")

# Internal router (endi asosiy app ichida)
internal_router = APIRouter(tags=["internal"])

@internal_router.post("/internal/refresh-cache")
async def refresh_cache_endpoint():
    """Internal endpoint for cache refresh."""
    from bot.utils.text_cache import refresh_cache
    count = await refresh_cache()
    return {"status": "ok", "refreshed": count}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Myestro API...")
    logger.info("Database tables are managed via Alembic migrations")
    logger.info(f"CORS Origins: {settings.ALLOWED_ORIGINS}")
   
    # Verify Redis connection
    try:
        import redis as redis_lib
        r = redis_lib.from_url(settings.REDIS_URL)
        r.ping()
        logger.info("Redis connection OK")
        r.close()
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    # Start cleanup scheduler
    def _nightly_cleanup():
        db = SessionLocal()
        try:
            run_full_cleanup(db)
        finally:
            db.close()

    scheduler.add_job(_nightly_cleanup, "cron", hour=3, minute=0, id="nightly_cleanup")
    scheduler.start()
    logger.info("🕒 Cleanup scheduler started (daily at 03:00 UTC)")

    yield

    # Shutdown
    logger.info("Shutting down Myestro API...")
    scheduler.shutdown(wait=False)
    await shutdown_ai_client()
    logger.info("AI client shut down.")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Myestro Backend API",
        description="AI-powered English learning platform",
        version="2.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Media fayllar uchun static serving
    media_dir = Path("/app/media")
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

    # Xavfsizlik: kodda yozilgan standart sirlar ishlatilayotgan bo'lsa ogohlantirish
    _KNOWN_DEFAULT_SECRET = "b376f24c1d2bfbaacfa9ef51027b74f40cb3aa9a8497aa50dd38c52c6bff5d07"
    if _KNOWN_DEFAULT_SECRET in (settings.JWT_ACCESS_SECRET, settings.JWT_REFRESH_SECRET):
        logger.critical(
            "🚨 JWT sirlari kodda yozilgan standart qiymatda! Har kim admin token yasay oladi. "
            "Railway'da JWT_ACCESS_SECRET va JWT_REFRESH_SECRET ni yangi tasodifiy qiymatga almashtiring."
        )
    if not settings.INTERNAL_API_KEY:
        logger.warning("⚠️ INTERNAL_API_KEY bo'sh — bot→backend endpointlari himoyasiz.")

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Routers
    app.include_router(tests_import.router, prefix="/api")  
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(websocket_router)
    app.include_router(content.router)
    app.include_router(stats.router)
    app.include_router(admin.router)
    app.include_router(ai_assistant.router)
    app.include_router(sync.router)
    app.include_router(knowledge.router)
    app.include_router(settings_router.router)
    app.include_router(bot_text.router)
    app.include_router(tests.router)
    app.include_router(admin_messages.router)
    app.include_router(broadcast.router)
    app.include_router(inbox.router)
    app.include_router(logs.router)
    app.include_router(ws_router)
    app.include_router(exam_v2_router)
    app.include_router(internal_router)

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "detail": "Internal server error",
                "status_code": 500,
            },
        )

    # Health check
    @app.get("/health", tags=["system"])
    async def health_check():
        """Service health status."""
        return {
            "status": "ok",
            "service": "myestro-backend",
            "version": "2.1.0"
        }

    return app


app = create_app()