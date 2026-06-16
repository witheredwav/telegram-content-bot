import random
from aiogram import Router, F, types
from aiogram.filters import CommandStart

import db
import keyboards as kb
from config import ADMIN_ID, CHANNEL_ID, LOG_CHAT

router = Router()

pending = {}
stats = {"created": 0, "used": 0}


def is_admin(user_id):
    return user_id == ADMIN_ID


def generate_code():
    while True:
        code = str(random.randint(10000, 99999))
        if not db.get_code(code):
            return code


# ================= START =================

@router.message(CommandStart())
async def start(message: types.Message):

    db.add_user(message.from_user.id)

    if is_admin(message.from_user.id):
        await message.answer("👑 Админ панель", reply_markup=kb.admin_kb())
    else:
        await message.answer("👋 Добро пожаловать", reply_markup=kb.user_kb())


# ================= NEW CODE =================

@router.message(F.text == "🎲 Новый код")
async def new_code(message: types.Message):

    if not is_admin(message.from_user.id):
        return

    code = generate_code()
    pending[message.from_user.id] = code
    stats["created"] += 1

    await message.answer(f"🎲 Код: {code}\nОтправь текст/ссылку/файл")


# ================= UPLOAD =================

@router.message()
async def upload(message: types.Message):

    if message.from_user.id not in pending:
        return

    code = pending[message.from_user.id]

    if message.document:
        db.create_code(code, "file", message.document.file_id)

    elif message.text.startswith(("http://", "https://")):
        db.create_code(code, "link", message.text)

    else:
        db.create_code(code, "text", message.text)

    del pending[message.from_user.id]

    await message.answer("✅ Сохранено")


# ================= USER REDEEM =================

@router.message()
async def redeem(message: types.Message):

    if is_admin(message.from_user.id):
        return

    db.add_user(message.from_user.id)

    code = db.get_code(message.text)

    if not code:
        await message.answer("❌ Код не найден")
        return

    type_, value, used = code

    if used:
        await message.answer("⚠️ Код уже использован")
        return

    db.mark_used(message.text)

    stats["used"] += 1

    if type_ == "text":
        await message.answer(value)

    elif type_ == "link":
        await message.answer(f"🔗 {value}")

    elif type_ == "file":
        await message.answer_document(value)
