import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN
from database import create_tables

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

async def on_startup():
print("Бот запущен")
await create_tables()

async def main():
await on_startup()
await dp.start_polling(bot)

if **name** == "**main**":
asyncio.run(main())
