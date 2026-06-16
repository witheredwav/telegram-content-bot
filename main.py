import asyncio
from aiogram import Bot, Dispatcher

from app.utils.config import settings
from app.handlers.start import router as start_router
from app.database.migrate import run_migrations

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start_router)


async def main():
    await run_migrations()

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
