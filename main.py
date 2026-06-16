import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio
from config import BOT_TOKEN, CHANNEL_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# загрузка кодов
def load_codes():
    with open("codes.json", "r", encoding="utf-8") as f:
        return json.load(f)

codes = load_codes()


# проверка подписки
async def is_subscribed(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


@dp.message(CommandStart())
async def start(message: types.Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("❌ Подпишись на канал и нажми /start снова.")
        return

    await message.answer("Введи код из поста или видео 👇")


@dp.message()
async def handle_code(message: types.Message):
    code = message.text.strip()

    if not await is_subscribed(message.from_user.id):
        await message.answer("❌ Сначала подпишись на канал.")
        return

    if code not in codes:
        await message.answer("❌ Неверный код.")
        return

    data = codes[code]

    if data["type"] == "file":
        await message.answer_document(types.FSInputFile(data["value"]))

    elif data["type"] == "text":
        await message.answer(data["value"])

    elif data["type"] == "link":
        await message.answer(f"🔗 Ссылка: {data['value']}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
