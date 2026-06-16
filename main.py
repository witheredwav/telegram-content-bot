import asyncio
import json
import random

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage


# ======================
# 🔐 НАСТРОЙКИ
# ======================

BOT_TOKEN = "8586166190:AAHOAcP29AYDThbBn5TN60ZeP7RQfhfeEe8"
CHANNEL_ID = "@witheredoff"
ADMIN_ID = 793806918


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ======================
# 📦 ДАННЫЕ
# ======================

def load_codes():
    try:
        with open("codes.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_codes(data):
    with open("codes.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

codes = load_codes()

pending = {}

stats = {
    "created": 0,
    "used": 0,
    "users": set()
}


# ======================
# 🎲 КОД
# ======================

def generate_code():
    return str(random.randint(10000, 99999))


# ======================
# 🔐 ПОДПИСКА
# ======================

async def is_subscribed(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# ======================
# 👑 АДМИН
# ======================

def is_admin(user_id: int):
    return user_id == ADMIN_ID


# ======================
# 📌 /start (НОВАЯ СИСТЕМА КНОПОК)
# ======================

@dp.message(CommandStart())
async def start(message: types.Message):

    stats["users"].add(message.from_user.id)

    if is_admin(message.from_user.id):
        kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🎲 Новый код")],
                [types.KeyboardButton(text="📋 Коды")],
                [types.KeyboardButton(text="📊 Статистика")]
            ],
            resize_keyboard=True
        )

        await message.answer("👑 Админ панель", reply_markup=kb)
        return

    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔔 Подписаться")],
            [types.KeyboardButton(text="✅ Проверить подписку")]
        ],
        resize_keyboard=True
    )

    await message.answer("👋 Привет! Сначала подпишись на канал 👇", reply_markup=kb)


# ======================
# 🔔 ПОДПИСАТЬСЯ
# ======================

@dp.message(F.text == "🔔 Подписаться")
async def subscribe_btn(message: types.Message):
    await message.answer(f"👉 Подпишись сюда: {CHANNEL_ID}")


# ======================
# ✅ ПРОВЕРКА ПОДПИСКИ
# ======================

@dp.message(F.text == "✅ Проверить подписку")
async def check_sub(message: types.Message):

    if await is_subscribed(message.from_user.id):
        await message.answer("✅ Подписка подтверждена!\nТеперь введи код 🔑")
    else:
        await message.answer("❌ Ты ещё не подписан")


# ======================
# 🎲 СОЗДАНИЕ КОДА
# ======================

@dp.message(F.text == "🎲 Новый код")
async def new_code(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    code = generate_code()
    pending[message.from_user.id] = code

    stats["created"] += 1

    await message.answer(
        f"🎲 Код: {code}\n\n"
        "Отправь:\n"
        "📄 текст / 🔗 ссылку / 📁 файл"
    )


# ======================
# 📋 СПИСОК КОДОВ
# ======================

@dp.message(F.text == "📋 Коды")
async def list_codes(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    if not codes:
        await message.answer("Пусто")
        return

    text = "📦 Коды:\n\n"

    for k, v in codes.items():
        text += f"{k} → {v['type']}\n"

    await message.answer(text)


# ======================
# 📊 СТАТИСТИКА
# ======================

@dp.message(F.text == "📊 Статистика")
async def stats_handler(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        f"📊 Статистика:\n\n"
        f"🆕 Кодов создано: {stats['created']}\n"
        f"📥 Использовано: {stats['used']}\n"
        f"👤 Пользователей: {len(stats['users'])}"
    )


# ======================
# 📥 АДМИН ОТПРАВКА ДАННЫХ
# ======================

@dp.message()
async def admin_input(message: types.Message):

    if message.from_user.id in pending:

        code = pending[message.from_user.id]

        if message.document:
            value = message.document.file_id
            type_ = "file"
        else:
            text = message.text

            if text.startswith("http"):
                type_ = "link"
            else:
                type_ = "text"

            value = text

        codes[code] = {
            "type": type_,
            "value": value
        }

        save_codes(codes)

        del pending[message.from_user.id]

        await message.answer(f"✅ Код {code} сохранён!")

        return


# ======================
# 👤 ПОЛЬЗОВАТЕЛИ (ПОЧИНЕНО)
# ======================

@dp.message()
async def user_handler(message: types.Message):

    if is_admin(message.from_user.id):
        return

    stats["users"].add(message.from_user.id)

    if not await is_subscribed(message.from_user.id):
        await message.answer("❌ Сначала подпишись на канал")
        return

    code = message.text.strip()

    if code not in codes:
        await message.answer("❌ Ошибка: неизвестный код")
        return

    data = codes[code]

    stats["used"] += 1

    if data["type"] == "text":
        await message.answer(data["value"])

    elif data["type"] == "link":
        await message.answer(f"🔗 {data['value']}")

    elif data["type"] == "file":
        await message.answer_document(data["value"])


# ======================
# 🚀 ЗАПУСК
# ======================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
