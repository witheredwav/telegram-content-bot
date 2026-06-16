import asyncio
from app.bot import bot, dp
from app.handlers import start  # noqa
from app.database.migrate import run_migrations


async def main():
    await run_migrations()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
