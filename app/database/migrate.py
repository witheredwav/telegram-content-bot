from app.database.session import engine, Base


async def run_migrations():
    """
    Простая авто-инициализация таблиц без Alembic
    (для запуска на Railway новичку)
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database initialized successfully")
