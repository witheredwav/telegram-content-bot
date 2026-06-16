import asyncio
import json
import random
import string

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage


# =========================
# 🔐 НАСТРОЙКИ
# =========================

BOT_TOKEN = "8586166190:AAHOAcP29AYDThbBn5TN60ZeP7RQfhfeEe8"
CHANNEL_ID = "@witheredoff"
ADMIN_ID = 793806918


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# =========================
# 📦 БАЗА КОДОВ
# =========================

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


# =========================
# 🎲 ГЕНЕРАТОР КОДОВ
# =========================

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


pending = {}  # временно хранит код для админа


# =========================
# 🔐 ПОДПИСКА
# =========================

async def is_subscribed(user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# =========================
# 👑 АДМИН ПРОВЕРКА
# =========================

def is_admin(user_id: int):
    return user_id == ADMIN_ID


# =========================
# 📌 /start
# =========================

@dp.message(CommandStart())
async def start(message: types.Message):

    if is_admin(message.from_user.id):
        kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="🎲 Сгенерировать код")],
                [types.KeyboardButton(text="📋 Коды")]
            ],
            resize_keyboard=True
        )

        await message.answer("👑 Админ панель", reply_markup=kb)
        return

    if not await is_subscribed(message.from_user.id):
        await message.answer("❌ Подпишись на канал и нажми /start снова")
        return

    await message.answer("🔑 Введи код из поста")


# =========================
# 🎲 СГЕНЕРИРОВАТЬ КОД
# =========================

@dp.message(F.text == "🎲 Сгенерировать код")
async def gen_code(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    code = generate_code()
    pending[message.from_user.id] = code

    await message.answer(
        f"🎲 Код создан: {code}\n\n"
        "Теперь отправь:\n"
        "📄 текст / 🔗 ссылку / 📁 файл"
    )


# =========================
# 📋 СПИСОК КОДОВ
# =========================

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


# =========================
# 📥 ЗАПИСЬ ДАННЫХ ОТ АДМИНА
# =========================

@dp.message()
async def admin_capture(message: types.Message):

    user_id = message.from_user.id

    if user_id not in pending:
        return

    code = pending[user_id]

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

    del pending[user_id]

    await message.answer(f"✅ Код {code} сохранён!")


# =========================
# 🔑 ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ
# =========================

@dp.message()
async def user_codes(message: types.Message):

    if is_admin(message.from_user.id):
        return

    if not await is_subscribed(message.from_user.id):
        await message.answer("❌ Сначала подпишись на канал")
        return

    code = message.text.strip()

    if code not in codes:
        await message.answer("❌ Неверный код")
        return

    data = codes[code]

    if data["type"] == "text":
        await message.answer(data["value"])

    elif data["type"] == "link":
        await message.answer(f"🔗 {data['value']}")

    elif data["type"] == "file":
        await message.answer_document(data["value"])


# =========================
# 🚀 ЗАПУСК
# =========================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
