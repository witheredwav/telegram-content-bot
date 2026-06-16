import asyncio

from aiogram import Dispatcher

from app.bot import bot
from app.utils.logger import logger


async def main() -> None:
    logger.info("Starting bot...")

    dp = Dispatcher()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
