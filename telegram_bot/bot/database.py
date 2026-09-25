import ssl as ssl_lib

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config import settings


def _build_engine():
    connect_args = {}

    # Railway public proxy uchun SSL (asyncpg faqat SSLContext qabul qiladi)
    if settings.DB_NEEDS_SSL:
        ctx = ssl_lib.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl_lib.CERT_NONE   # sslmode=require ekvivalenti
        connect_args["ssl"] = ctx

    return create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_recycle=1800,
        connect_args=connect_args,
    )


engine = _build_engine()
async_session = async_sessionmaker(engine, expire_on_commit=False)