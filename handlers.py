import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *
from keyboards import start_kb, menu_kb, admin_kb

router = Router()

pending = {}


# ================= START =================
@router.message(F.text.startswith("/start"))
async def start(msg: Message):

    await add_user(msg.from_user.id)
    await add_stat("start")

    await msg.answer("👋 Добро пожаловать", reply_markup=start_kb())


# ================= CHECK SUB =================
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

    await add_stat("check")

    member = await cb.bot.get_chat_member(
        f"@{CHANNEL_USERNAME}",
        cb.from_user.id
    )

    if member.status not in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    ]:
        await cb.message.answer("❌ Нет подписки")
        return

    await cb.message.answer("✅ Доступ открыт", reply_markup=menu_kb())


# ================= CODE =================
@router.callback_query(F.data == "code")
async def code(cb: CallbackQuery):
    await cb.message.answer("🔑 Введите 5-значный код")


@router.message(F.text.regexp(r"^\d{5}$"))
async def enter_code(msg: Message):

    await add_stat("code")

    data = await get_code(msg.text)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(f"📦 Контент:\n\n{data[1]}")


# ================= ADMIN PANEL =================
@router.message(F.text == "/admin")
async def admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 SAAS PANEL", reply_markup=admin_kb())


# ================= STATS =================
@router.callback_query(F.data == "admin_stats")
async def stats(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    text = f"""
📊 STATISTICS

👤 Users: {await users_count() or 0}
📦 Codes: {await codes_count() or 0}

start: {await get_stat("start") or 0}
check: {await get_stat("check") or 0}
code: {await get_stat("code") or 0}
"""

    await cb.message.answer(text.strip())


# ================= CODES LIST (BUTTONS) =================
@router.callback_query(F.data == "admin_codes")
async def codes(cb: CallbackQuery):

    data = await get_all_codes_full()

    if not data:
        await cb.message.answer("❌ Нет кодов")
        return

    kb = []

    for code, content in data:
        kb.append([
            InlineKeyboardButton(
                text=f"🔑 {code}",
                callback_data=f"del_code:{code}"
            )
        ])

    await cb.message.answer(
        "📦 КОДЫ (нажми для удаления)",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


# ================= DELETE CODE =================
@router.callback_query(F.data.startswith("del_code:"))
async def del_code(cb: CallbackQuery):

    code = cb.data.split(":")[1]

    await delete_code_db(code)

    await cb.message.answer(f"🗑 Код {code} удалён")


# ================= CREATE CODE =================
@router.callback_query(F.data == "admin_create")
async def create(cb: CallbackQuery):

    code = str(random.randint(10000, 99999))
    pending[cb.from_user.id] = code

    await cb.message.answer(f"🎲 Код: {code}\nОтправь текст")


@router.message()
async def save(msg: Message):

    if msg.from_user.id not in pending:
        return

    code = pending[msg.from_user.id]

    await add_code(code, msg.text)

    pending.pop(msg.from_user.id)

    await msg.answer("✅ Сохранено")


# ================= REF SYSTEM =================
@router.callback_query(F.data == "admin_refs")
async def refs(cb: CallbackQuery):

    data = await get_all_refs()

    if not data:
        await cb.message.answer("❌ Нет рефералов")
        return

    kb = []

    for user_id, code, invites in data:
        kb.append([
            InlineKeyboardButton(
                text=f"👤 {user_id} | {invites}",
                callback_data=f"ref_open:{user_id}"
            )
        ])

    await cb.message.answer(
        "👥 РЕФЕРАЛЫ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@router.callback_query(F.data.startswith("ref_open:"))
async def ref_open(cb: CallbackQuery):

    user_id = int(cb.data.split(":")[1])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Сброс", callback_data=f"ref_reset:{user_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"ref_del:{user_id}")
        ]
    ])

    await cb.message.answer(f"👤 USER {user_id}", reply_markup=kb)


@router.callback_query(F.data.startswith("ref_reset:"))
async def ref_reset(cb: CallbackQuery):

    user_id = int(cb.data.split(":")[1])

    await reset_ref(user_id)

    await cb.message.answer("🔄 Сброшено")


@router.callback_query(F.data.startswith("ref_del:"))
async def ref_del(cb: CallbackQuery):

    user_id = int(cb.data.split(":")[1])

    async with aiosqlite.connect("db.sqlite3") as db:
        await db.execute("DELETE FROM referrals WHERE user_id=?", (user_id,))
        await db.commit()

    await cb.message.answer("🗑 Удалено")
