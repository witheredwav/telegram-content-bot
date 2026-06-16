import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import CHANNEL_USERNAME, ADMIN_ID
from db import add_code, get_code, users_count, codes_count
from keyboards import start_kb, menu_kb

router = Router()

pending_code = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):
    await msg.answer(
        "👋 Привет!\n\nПодпишись на канал",
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


# ================= ENTER CODE =================
@router.callback_query(F.data == "code")
async def enter_code(cb: CallbackQuery):
    await cb.message.answer("🔑 Введите код:")
    await cb.answer()


# ================= CHECK USER CODE =================
@router.message(F.text.regexp(r"^\d{5}$"))
async def check_code(msg: Message):

    code = msg.text.strip()

    data = await get_code(code)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    content_type = data[1]
    content = data[2]

    if content_type == "text":
        await msg.answer(content)

    elif content_type == "photo":
        await msg.answer_photo(photo=content)

    elif content_type == "video":
        await msg.answer_video(video=content)

    elif content_type == "document":
        await msg.answer_document(document=content)

    else:
        await msg.answer("❌ Ошибка контента")


# ================= ADMIN PANEL =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        "👑 АДМИНКА\n\n"
        "/create_code - создать код\n"
        "/delete_code 12345 - удалить код\n"
        "/stats - статистика"
    )


# ================= CREATE CODE =================
@router.message(F.text == "/create_code")
async def create_code(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(0, 99999)).zfill(5)

    pending_code[msg.from_user.id] = code

    await msg.answer(
        f"🎲 Код создан: {code}\n\n"
        "Отправь контент (текст / фото / видео / файл)"
    )


# ================= SAVE CONTENT =================
@router.message(F.from_user.id == ADMIN_ID)
async def save_content(msg: Message):

    code = pending_code.get(msg.from_user.id)

    if not code:
        return

    content_type = None
    content = None

    if msg.photo:
        content_type = "photo"
        content = msg.photo[-1].file_id

    elif msg.video:
        content_type = "video"
        content = msg.video.file_id

    elif msg.document:
        content_type = "document"
        content = msg.document.file_id

    elif msg.text:
        content_type = "text"
        content = msg.text

    else:
        await msg.answer("❌ Неизвестный формат")
        return

    await add_code(code, content_type, content)

    pending_code.pop(msg.from_user.id)

    await msg.answer(f"✅ Код {code} сохранён!")


# ================= DELETE CODE =================
@router.message(F.text.regexp(r"^/delete_code"))
async def delete_code(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) < 2:
        await msg.answer("❌ Используй: /delete_code 12345")
        return

    code = parts[1]

    # удаление
    import aiosqlite

    async with aiosqlite.connect("db.sqlite3") as db:
        await db.execute("DELETE FROM codes WHERE code=?", (code,))
        await db.commit()

    await msg.answer(f"🗑 Код {code} удалён")


# ================= STATS FIX =================
@router.message(F.text.regexp(r"^/stats"))
async def stats(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    users = await users_count()
    codes = await codes_count()

    await msg.answer(
        "📊 СТАТИСТИКА\n\n"
        f"👤 Пользователей: {users}\n"
        f"🔑 Кодов: {codes}"
    )
