from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.utils.config import settings

# 🔥 ВАЖНО: Railway Postgres требует SSL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
