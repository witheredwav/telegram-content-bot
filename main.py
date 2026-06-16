import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from db import init_db
from handlers import router


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    await init_db()

    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
