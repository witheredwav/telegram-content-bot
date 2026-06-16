from sqlalchemy.ext.asyncio import create_async_engine
from app.utils.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://"
    )

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"timeout": 10},
)


async def run_migrations():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        raise
