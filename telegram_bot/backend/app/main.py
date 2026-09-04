import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import close_redis
from app.core.exceptions import AppException
from app.api import bot_text

# Add telegram_bot root to path so shared module is importable
_telegram_bot_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _telegram_bot_root not in sys.path:
    sys.path.insert(0, _telegram_bot_root)

from app.config import settings
from app.api import (
    auth, users, content, broadcast, inbox, settings as settings_router,
    stats, knowledge, ai_assistant, admin, sync, bot_text, admin_messages, logs, tests
)
from app.websocket.admin_ws import router as ws_router
from app.core.exceptions import AppException
from app.services.ai_service import shutdown_ai_client

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.exam_v2.router import exam_v2_router

# Bot uchun mini FastAPI app (internal endpoints)
internal_app = FastAPI()

@internal_app.post("/internal/refresh-cache")
async def refresh_cache_endpoint():
    """
    Internal endpoint for cache refresh.
    Called by backend when bot texts are updated.
    """
    from bot.utils.text_cache import refresh_cache
    count = await refresh_cache()
    return {"status": "ok", "refreshed": count}

# Start internal app on separate port
import uvicorn
from threading import Thread

def run_internal_app():
    uvicorn.run(internal_app, host="0.0.0.0", port=8001, log_level="error")

# Start in background thread
internal_thread = Thread(target=run_internal_app, daemon=True)
internal_thread.start()


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

    yield

    logger.info("Shutting down Myestro API...")
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3002",
            "http://localhost:3003",
            "http://localhost:3001",
            "http://localhost:8002",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:3003",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Exam v2 router
    app.include_router(exam_v2_router)
    
    # Include routers
    app.include_router(auth.router)
    app.include_router(users.router)
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