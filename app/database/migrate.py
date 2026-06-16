from app.database.session import engine, Base


async def run_migrations():
    """
    Простое создание таблиц без Alembic
    Работает с SQLAlchemy async правильно
    """

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully")
