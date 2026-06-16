import asyncio

from aiogram import Dispatcher

from app.bot import bot
from app.utils.logger import logger

from app.database.migrate import run_migrations
from app.database.session import engine
from app.database.redis import redis

from app.handlers.start import router as start_router


async def main():

    logger.info("Bot starting...")

    run_migrations()

    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)

    await redis.ping()

    dp = Dispatcher()

    dp.include_router(start_router)

    logger.info("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
