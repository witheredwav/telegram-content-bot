import asyncio
from alembic import command
from alembic.config import Config
from app.database.session import engine


async def run_migrations():
    # 🔥 даём Railway Postgres время подняться
    await asyncio.sleep(5)

    try:
        alembic_cfg = Config("alembic.ini")

        # синхронный вызов внутри async окружения
        command.upgrade(alembic_cfg, "head")

    except Exception as e:
        print(f"[MIGRATIONS ERROR] {e}")
        # не валим весь бот
