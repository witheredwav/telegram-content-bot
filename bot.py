import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN
from database import create_tables

from handlers.start import router as start_router

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

async def on_startup():
print("Бот запущен")
await create_tables()

async def main():

await on_startup()

dp.include_router(start_router)

await dp.start_polling(bot)

if **name** == "**main**":
asyncio.run(main())
