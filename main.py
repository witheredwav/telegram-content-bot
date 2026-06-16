import asyncio

from app.bot import bot, dp
from app.utils.logger import logger
from app.database.migrate import run_migrations

from app.handlers.start import router as start_router
from app.handlers.referrals import router as referrals_router


async def main():
    logger.info("Starting bot...")

    # 🔥 1. миграции (не валят бот если упали)
    try:
        await run_migrations()
    except Exception as e:
        logger.error(f"Migrations failed: {e}")

    # 🔥 2. подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(referrals_router)

    # 🔥 3. старт бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
