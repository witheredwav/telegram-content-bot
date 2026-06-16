from db import add_stat


import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
        "👋 Привет!\nПодпишись на канал 👇",
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


# ================= CODE INPUT =================
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


# ================= ADMIN MENU BUTTON =================
def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="📦 Все коды", callback_data="codes")],
        [InlineKeyboardButton(text="🗑 Удалить код", callback_data="delete_menu")],
        [InlineKeyboardButton(text="🎲 Создать код", callback_data="create_code")]
    ])


# ================= OPEN ADMIN =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 Админ-панель:", reply_markup=admin_panel_kb())


# ================= STATS BUTTON =================
@router.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    await cb.message.answer(
        f"👤 Users: {await users_count()}\n"
        f"🔑 Codes: {await codes_count()}"
    )

    await cb.answer()


# ================= SHOW CODES =================
@router.callback_query(F.data == "codes")
async def codes(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    data = await get_all_codes()

    if not data:
        await cb.message.answer("нет кодов")
        return

    text = "📦 КОДЫ:\n\n"
    for c in data:
        text += f"{c[0]}\n"

    await cb.message.answer(text)

    await cb.answer()


# ================= DELETE MENU =================
@router.callback_query(F.data == "delete_menu")
async def delete_menu(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    data = await get_all_codes()

    if not data:
        await cb.message.answer("нет кодов")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c[0], callback_data=f"del_{c[0]}")]
        for c in data
    ])

    await cb.message.answer("Выбери код для удаления:", reply_markup=kb)

    await cb.answer()


# ================= DELETE CODE BUTTON =================
@router.callback_query(F.data.startswith("del_"))
async def delete_code(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    code = cb.data.replace("del_", "")

    await delete_code_db(code)

    await cb.message.answer(f"🗑 Код {code} удалён")

    await cb.answer()


# ================= CREATE CODE =================
@router.callback_query(F.data == "create_code")
async def create_code(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    code = str(random.randint(0, 99999)).zfill(5)
    pending[cb.from_user.id] = code

    await cb.message.answer(f"🎲 Код: {code}\nТеперь отправь контент")

    await cb.answer()


# ================= SAVE CONTENT =================
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

    await msg.answer("✅ Сохранено")
