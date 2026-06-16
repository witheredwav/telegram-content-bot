import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.utils.config import settings
from app.database.migrate import run_migrations

from app.handlers.start import router as start_router
from app.handlers.referrals import router as referrals_router


async def main():
    # Логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    print("Starting bot...")

    # 1. Инициализация базы данных
    await run_migrations()

    print("Database ready")

    # 2. Создаём бота
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # 3. Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(referrals_router)

    # 4. Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
