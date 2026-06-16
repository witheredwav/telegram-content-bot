import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram import types

from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Бот работает ✅")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
