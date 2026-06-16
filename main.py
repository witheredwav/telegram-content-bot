import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from db import init
from handlers import router

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

async def main():
    await init()
    dp.include_router(router)

    print("BOT STARTED")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
