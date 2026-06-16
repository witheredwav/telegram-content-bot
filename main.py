import asyncio

from aiogram import Dispatcher
from sqlalchemy import text

from app.bot import bot

from app.database.session import engine
from app.database.redis import redis

from app.utils.logger import logger


async def check_postgres() -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text("SELECT 1")
        )

    logger.info("PostgreSQL connected")


async def check_redis() -> None:
    await redis.ping()

    logger.info("Redis connected")


async def main() -> None:

    logger.info("Starting bot...")

    await check_postgres()
    await check_redis()

    dp = Dispatcher()

    logger.info("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
