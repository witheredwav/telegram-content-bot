import random
from aiogram import Router, F
from aiogram.types import Message

from config import ADMIN_ID
from db import (
    add_user,
    add_code,
    get_code,
    users_count,
    codes_count,
    get_all_codes,
    delete_code_db
)

router = Router()

pending = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):
    await add_user(msg.from_user.id)
    await msg.answer("бот работает")


# ================= CREATE CODE =================
@router.message(F.text == "/create_code")
async def create(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(0, 99999)).zfill(5)
    pending[msg.from_user.id] = code

    await msg.answer(f"код: {code}\nотправь контент")


# ================= SAVE CONTENT (СТРОГО ТОЛЬКО ДЛЯ pending) =================
@router.message()
async def save(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = pending.get(msg.from_user.id)
    if not code:
        return

    if msg.photo:
        await add_code(code, "photo", msg.photo[-1].file_id)
    elif msg.video:
        await add_code(code, "video", msg.video.file_id)
    elif msg.document:
        await add_code(code, "document", msg.document.file_id)
    elif msg.text and not msg.text.startswith("/"):
        await add_code(code, "text", msg.text)
    else:
        return

    pending.pop(msg.from_user.id)

    await msg.answer("сохранено")


# ================= CHECK CODE =================
@router.message(F.text.regexp(r"^\d{5}$"))
async def check(msg: Message):

    data = await get_code(msg.text)

    if not data:
        await msg.answer("неверный код")
        return

    t = data[1]
    c = data[2]

    if t == "text":
        await msg.answer(c)
    elif t == "photo":
        await msg.answer_photo(c)
    elif t == "video":
        await msg.answer_video(c)
    elif t == "document":
        await msg.answer_document(c)


# ================= STATS =================
@router.message(F.text == "/stats")
async def stats(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        f"users: {await users_count()}\n"
        f"codes: {await codes_count()}"
    )


# ================= CODES =================
@router.message(F.text == "/codes")
async def codes(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    data = await get_all_codes()

    text = ""
    for c in data:
        text += c[0] + "\n"

    await msg.answer(text if text else "нет кодов")


# ================= DELETE =================
@router.message(F.text.startswith("/delete_code"))
async def delete(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) < 2:
        await msg.answer("пример: /delete_code 12345")
        return

    code = parts[1]

    await delete_code_db(code)
    await msg.answer("удалено (если существовал)")
