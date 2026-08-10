import redis.asyncio as redis
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base ,  Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

# Sync engine (existing)
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,

)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine (for async endpoints like settings.py)
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)

Base = declarative_base()

async def get_async_db():
    """FastAPI dependency — yields an async DB session per request."""
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


"""Database and Redis connection management."""

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# SYNC DATABASE (for backward compatibility)
# ═══════════════════════════════════════════════════════════════════

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Sync DB dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════
# ASYNC DATABASE
# ═══════════════════════════════════════════════════════════════════

async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=10,
    max_overflow=20,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db() -> AsyncSession:
    """Async DB dependency."""
    async with AsyncSessionLocal() as session:
        yield session


# ═══════════════════════════════════════════════════════════════════
# REDIS CONNECTION
# ═══════════════════════════════════════════════════════════════════

_redis_client: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get Redis client (singleton pattern)."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = await redis.from_url(
            settings.REDIS_URL,
            db=0,  # Backend uses DB 0
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
        logger.info("Redis client initialized")
    
    return _redis_client


async def close_redis():
    """Close Redis connection (call in app shutdown)."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")


# ═══════════════════════════════════════════════════════════════════
# ORM BASE
# ═══════════════════════════════════════════════════════════════════

from sqlalchemy.orm import declarative_base

Base = declarative_base()