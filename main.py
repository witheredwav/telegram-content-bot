import asyncio

from aiogram import Dispatcher

from app.bot import bot
from app.utils.logger import logger

from app.database.migrate import run_migrations

# USER
from app.handlers.start import router as start_router
from app.handlers.subscription import router as subscription_router
from app.handlers.menu import router as menu_router
from app.handlers.works import router as works_router
from app.handlers.referrals import router as referrals_router
from app.handlers.request import router as request_router
from app.handlers.code import router as code_router
from app.handlers.request_flow import router as request_flow_router

# ADMIN
from app.handlers.admin.admin_menu import router as admin_router
from app.handlers.admin.create_code import router as admin_create_router
from app.handlers.admin.stats import router as stats_router
from app.handlers.admin.requests_admin import router as admin_requests_router
from app.handlers.admin.analytics import router as analytics_router


async def main():

    logger.info("Bot starting...")

    run_migrations()

    dp = Dispatcher()

    # USER
    dp.include_router(start_router)
    dp.include_router(subscription_router)
    dp.include_router(menu_router)
    dp.include_router(works_router)
    dp.include_router(referrals_router)
    dp.include_router(request_router)
    dp.include_router(code_router)
    dp.include_router(request_flow_router)

    # ADMIN
    dp.include_router(admin_router)
    dp.include_router(admin_create_router)
    dp.include_router(stats_router)
    dp.include_router(admin_requests_router)
    dp.include_router(analytics_router)

    logger.info("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
