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
    delete_code_db,
    add_stat
)

from keyboards import start_kb, menu_kb

router = Router()
pending = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):
    await add_user(msg.from_user.id)
    await add_stat("start")

    await msg.answer(
        "👋 Привет!\nПодпишись на канал 👇",
        reply_markup=start_kb()
    )


# ================= CHECK SUB =================
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
            await cb.message.answer("✅ Подписка подтверждена", reply_markup=menu_kb())
        else:
            await cb.message.answer("❌ Вы не подписаны")

    except:
        await cb.message.answer("❌ Ошибка проверки")

    await cb.answer()


# ================= CODE BUTTON =================
@router.callback_query(F.data == "code")
async def code_btn(cb: CallbackQuery):
    await add_stat("code_click")

    await cb.message.answer("🔑 Введите 5-значный код:")
    await cb.answer()


# ================= ENTER CODE =================
@router.message(F.text.regexp(r"^\d{5}$"))
async def check_code(msg: Message):

    await add_stat("code_enter")

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
def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="📦 Все коды", callback_data="codes")],
        [InlineKeyboardButton(text="🗑 Удалить код", callback_data="del_menu")],
        [InlineKeyboardButton(text="🎲 Создать код", callback_data="create")]
    ])


# ================= ADMIN OPEN =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 Админ-панель", reply_markup=admin_kb())


# ================= STATS =================
@router.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    await add_stat("admin_stats")

    await cb.message.answer(
        f"""📊 СТАТИСТИКА

👤 Users: {await users_count()}
🔑 Codes: {await codes_count()}
"""
    )

    await cb.answer()


# ================= ALL CODES =================
@router.callback_query(F.data == "codes")
async def codes(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    data = await get_all_codes()

    if not data:
        await cb.message.answer("📭 Нет кодов")
        return

    text = "📦 КОДЫ:\n\n"
    for c in data:
        text += f"{c[0]}\n"

    await cb.message.answer(text)

    await cb.answer()


# ================= DELETE MENU =================
@router.callback_query(F.data == "del_menu")
async def del_menu(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    data = await get_all_codes()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c[0], callback_data=f"del_{c[0]}")]
        for c in data
    ])

    await cb.message.answer("Выбери код:", reply_markup=kb)
    await cb.answer()


# ================= DELETE CODE =================
@router.callback_query(F.data.startswith("del_"))
async def delete(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    code = cb.data.replace("del_", "")

    await delete_code_db(code)
    await add_stat("delete_code")

    await cb.message.answer(f"🗑 Удалено: {code}")
    await cb.answer()


# ================= CREATE CODE =================
@router.callback_query(F.data == "create")
async def create(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("нет доступа", show_alert=True)

    code = str(random.randint(0, 99999)).zfill(5)
    pending[cb.from_user.id] = code

    await cb.message.answer(f"🎲 Код: {code}\nОтправь контент")
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

    await add_stat("code_created")

    await msg.answer("✅ Сохранено")
