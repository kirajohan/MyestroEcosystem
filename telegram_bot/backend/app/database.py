import logging
import redis.asyncio as redis

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# 1. ORM BASE
# ═══════════════════════════════════════════════════════════════════
Base = declarative_base()
Base.metadata.create_all = lambda *args, **kwargs: None  # Prevent errors on re-import


# ═══════════════════════════════════════════════════════════════════
# 2. ASYNC DATABASE (FastAPI uchun asosiy tavsiya etiladigan usul)
# ═══════════════════════════════════════════════════════════════════
# URL ni asyncpg uchun to'g'ri formatga o'tkazamiz
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,  # SQL so'rovlarni ko'rish uchun True qiling (debug paytida)
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # MUHIM: Async da commit dan keyin xatolik bo'lmasligi uchun
)


async def get_async_db() -> AsyncSession:
    """
    FastAPI dependency: Har bir so'rov uchun async DB sessiyasini taqdim etadi.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ═══════════════════════════════════════════════════════════════════
# 3. SYNC DATABASE (Faqat Alembic migratsiyalari yoki maxsus sync skriptlar uchun)
# ═══════════════════════════════════════════════════════════════════
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Session:
    """
    FastAPI dependency: Sync DB sessiyasi (faqat zarurat bo'lganda ishlatilsin).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════
# 4. REDIS CONNECTION
# ═══════════════════════════════════════════════════════════════════
_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Redis klientini olish (lazy initialization)."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            db=0,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
        logger.info("✅ Redis client initialized")
    
    return _redis_client


async def close_redis():
    """Ilovani o'chirish (shutdown) paytida Redis ulanishini yopish."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("🔴 Redis client closed")