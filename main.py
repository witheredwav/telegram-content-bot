import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from db import init_db
from handlers import router


async def main():

    # ================= LOGGING =================
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    # ================= BOT =================
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    # ================= DISPATCHER =================
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)

    # ================= DB INIT =================
    await init_db()

    print("✅ BOT STARTED SUCCESSFULLY")

    # ================= START POLLING =================
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
