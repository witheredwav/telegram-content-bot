import random
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID, CHANNEL_USERNAME
from db import (
    add_user, add_code, get_code,
    users_count, codes_count,
    get_all_codes, delete_code_db,
    add_stat, get_stat
)

from keyboards import start_kb, menu_kb, admin_kb


router = Router()
pending = {}
user_cooldown = {}


# ================== ANTI SPAM ==================
def check_spam(user_id: int):
    now = datetime.now()
    if user_id in user_cooldown:
        if now - user_cooldown[user_id] < timedelta(seconds=2):
            return False
    user_cooldown[user_id] = now
    return True


# ================== START ==================
@router.message(F.text == "/start")
async def start(msg: Message):

    if not check_spam(msg.from_user.id):
        return

    await add_user(msg.from_user.id)
    await add_stat("start")

    await msg.answer(
        "👋 Добро пожаловать!\nПодпишись:",
        reply_markup=start_kb()
    )


# ================== CHECK SUB ==================
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

    await add_stat("check_click")

    try:
        member = await cb.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            cb.from_user.id
        )

        if member.status in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]:
            await cb.message.answer("✅ Подписка есть", reply_markup=menu_kb())
        else:
            await cb.message.answer("❌ Нет подписки")
    except:
        await cb.message.answer("❌ Ошибка")

    await cb.answer()


# ================== CODE INPUT ==================
@router.callback_query(F.data == "code")
async def code(cb: CallbackQuery):

    await add_stat("code_click")
    await cb.message.answer("🔑 Введи 5-значный код")
    await cb.answer()


# ================== ENTER CODE ==================
@router.message(F.text.regexp(r"^\d{5}$"))
async def enter_code(msg: Message):

    if not check_spam(msg.from_user.id):
        return

    await add_stat("code_enter")

    data = await get_code(msg.text)

    if not data:
        await add_stat("wrong_code")
        await msg.answer("❌ Неверный код")
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


# ================== ADMIN ==================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 ADMIN", reply_markup=admin_kb())


# ================== STATS ==================
@router.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    text = f"""
📊 PRO STATS

👤 Users: {await users_count()}
🔑 Codes: {await codes_count()}

📈 Events:
start: {await get_stat("start")}
check: {await get_stat("check_click")}
open code: {await get_stat("code_click")}
enter: {await get_stat("code_enter")}
wrong: {await get_stat("wrong_code")}
created: {await get_stat("code_created")}
deleted: {await get_stat("delete_code")}
"""

    await cb.message.answer(text)
    await cb.answer()


# ================== LIST CODES ==================
@router.callback_query(F.data == "codes")
async def codes(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    data = await get_all_codes()

    text = "📦 CODES:\n\n"
    for c in data:
        text += f"{c[0]}\n"

    await cb.message.answer(text)
    await cb.answer()


# ================== CREATE CODE ==================
@router.callback_query(F.data == "create")
async def create(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(0, 99999)).zfill(5)
    pending[cb.from_user.id] = code

    await cb.message.answer(f"🎲 Код: {code}\nОтправь контент")
    await cb.answer()


# ================== SAVE CONTENT ==================
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
    elif msg.text:
        await add_code(code, "text", msg.text)

    pending.pop(msg.from_user.id, None)
    await add_stat("code_created")

    await msg.answer("✅ Сохранено")


# ================== DELETE ==================
@router.callback_query(F.data.startswith("del_"))
async def delete(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    code = cb.data.replace("del_", "")

    await delete_code_db(code)
    await add_stat("delete_code")

    await cb.message.answer(f"🗑 Удалено: {code}")
