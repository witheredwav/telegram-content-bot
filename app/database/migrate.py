from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)


async def run_migrations():
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)  # пока пустой мигратор
