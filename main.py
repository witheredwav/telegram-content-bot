import asyncio

from aiogram import Dispatcher

from app.bot import bot
from app.utils.logger import logger

from app.database.migrate import run_migrations

from app.handlers.start import router as start_router
from app.handlers.subscription import router as subscription_router
from app.handlers.menu import router as menu_router
from app.handlers.works import router as works_router
from app.handlers.referrals import router as referrals_router
from app.handlers.request import router as request_router


async def main():

    logger.info("Bot starting...")

    run_migrations()

    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(subscription_router)
    dp.include_router(menu_router)
    dp.include_router(works_router)
    dp.include_router(referrals_router)
    dp.include_router(request_router)

    logger.info("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
