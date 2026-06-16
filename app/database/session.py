from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.utils.config import settings


# =========================
# BASE (для всех моделей)
# =========================
class Base(DeclarativeBase):
    pass


# =========================
# DATABASE ENGINE
# =========================
engine = create_async_engine(
    settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    ),
    echo=False,
)


# =========================
# SESSION FACTORY
# =========================
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =========================
# DEPENDENCY (если нужно)
# =========================
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
