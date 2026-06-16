import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import (
    add_user,
    add_code,
    get_code,
    users_count,
    codes_count,
    get_all_codes,
    delete_code_db
)

from keyboards import start_kb, menu_kb

router = Router()

pending = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):
    await add_user(msg.from_user.id)

    await msg.answer(
        "👋 Привет!\n\nПодпишись на канал 👇",
        reply_markup=start_kb()
    )


# ================= CHECK SUB =================
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

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
            await cb.message.answer("✅ Подписка подтверждена", reply_markup=menu_kb())
        else:
            await cb.message.answer("❌ Вы не подписаны")

    except:
        await cb.message.answer("❌ Ошибка проверки")

    await cb.answer()


# ================= OPEN CODE INPUT =================
@router.callback_query(F.data == "code")
async def enter_code(cb: CallbackQuery):
    await cb.message.answer("🔑 Введите 5-значный код:")
    await cb.answer()


# ================= CHECK CODE =================
@router.message(F.text.regexp(r"^\d{5}$"))
async def check_code(msg: Message):

    data = await get_code(msg.text)

    if not data:
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


# ================= ADMIN PANEL =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        "👑 АДМИНКА\n\n"
        "/create_code\n"
        "/delete_code 12345\n"
        "/stats\n"
        "/codes"
    )


# ================= CREATE CODE =================
@router.message(F.text == "/create_code")
async def create(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(0, 99999)).zfill(5)
    pending[msg.from_user.id] = code

    await msg.answer(f"🎲 Код: {code}\n\nОтправь контент")


# ================= SAVE CONTENT (SAFE) =================
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

    pending.pop(msg.from_user.id, None)

    await msg.answer("✅ Код сохранён")


# ================= DELETE CODE =================
@router.message(F.text.startswith("/delete_code"))
async def delete(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) < 2:
        await msg.answer("❌ /delete_code 12345")
        return

    code = parts[1]

    await delete_code_db(code)
    await msg.answer("🗑 Удалено (если существовал)")


# ================= STATS =================
@router.message(F.text == "/stats")
async def stats(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        f"👤 Users: {await users_count()}\n"
        f"🔑 Codes: {await codes_count()}"
    )


# ================= CODES =================
@router.message(F.text == "/codes")
async def codes(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    data = await get_all_codes()

    if not data:
        await msg.answer("📭 Нет кодов")
        return

    text = "📦 КОДЫ:\n\n"
    for c in data:
        text += f"{c[0]}\n"

    await msg.answer(text)
