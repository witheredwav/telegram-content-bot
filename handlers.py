import random
from aiogram import Router, F, types
from aiogram.filters import CommandStart

import db
from config import ADMIN_ID, CHANNEL_ID, EXAMPLES_CHANNEL

router = Router()

pending = {}
stats = {"created": 0, "used": 0}


def is_admin(user_id):
    return user_id == ADMIN_ID


def generate_code():
    return str(random.randint(10000, 99999))


# ================= START =================

@router.message(CommandStart())
async def start(message: types.Message):

    db.add_user(message.from_user.id)

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
            [types.KeyboardButton(text="🔑 Ввести код")],
            [types.KeyboardButton(text="🎬 Примеры")]
        ],
        resize_keyboard=True
    )

    await message.answer("👋 Меню", reply_markup=kb)


# ================= НОВЫЙ КОД =================

@router.message(F.text == "🎲 Новый код")
async def new_code(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    code = generate_code()
    pending[message.from_user.id] = code
    stats["created"] += 1

    await message.answer(f"Код: {code}\nОтправь текст/ссылку/файл")


# ================= ЗАГРУЗКА =================

@router.message()
async def upload(message: types.Message):

    if message.from_user.id not in pending:
        return

    code = pending[message.from_user.id]

    if message.document:
        db.add_code(code, "file", message.document.file_id)

    elif message.text.startswith("http"):
        db.add_code(code, "link", message.text)

    else:
        db.add_code(code, "text", message.text)

    del pending[message.from_user.id]

    await message.answer("Сохранено ✅")


# ================= ПОЛЬЗОВАТЕЛЬ =================

@router.message()
async def user(message: types.Message):

    if is_admin(message.from_user.id):
        return

    db.add_user(message.from_user.id)

    code = db.get_code(message.text)

    if not code:
        await message.answer("❌ неверный код")
        return

    type_, value = code
    stats["used"] += 1

    if type_ == "text":
        await message.answer(value)

    elif type_ == "link":
        await message.answer(f"🔗 {value}")

    elif type_ == "file":
        await message.answer_document(value)
