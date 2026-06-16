from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.utils.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,

    # 🔥 ВАЖНО ДЛЯ RAILWAY
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,

    connect_args={
        "ssl": "require"
    },
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
