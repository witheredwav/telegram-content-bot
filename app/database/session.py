from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.utils.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
