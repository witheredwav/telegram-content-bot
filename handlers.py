import aiosqlite

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *

router = Router()

pending = {}
pending_delete = {}
pending_ref_state = {}


# ================= START =================
@router.message(F.text.startswith("/start"))
async def start(msg: Message):

    await add_user(msg.from_user.id)
    await add_event(msg.from_user.id, "start")

    await msg.answer("👋 Добро пожаловать")


# ================= CHECK SUB =================
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

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

    await cb.message.answer("✅ Доступ открыт")


# ================= CODE INPUT =================
@router.message(F.text.regexp(r"^\d{5}$"))
async def code_input(msg: Message):

    await add_event(msg.from_user.id, f"code:{msg.text}")

    data = await get_code(msg.text)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(f"📦 Контент:\n{data[1]}")


# ================= REF BUTTON =================
@router.callback_query(F.data == "ref")
async def ref(cb: CallbackQuery):

    await add_event(cb.from_user.id, "ref_open")

    pending_ref_state[cb.from_user.id] = True

    await cb.message.answer("👥 Введите реф-код:")


# ================= REF INPUT =================
@router.message()
async def any_message(msg: Message):

    # ================= REF FLOW =================
    if pending_ref_state.get(msg.from_user.id):

        code = msg.text.strip()

        ok = await add_ref_if_valid(msg.from_user.id, code)

        if not ok:
            await msg.answer("❌ Реферал не засчитан")
            pending_ref_state.pop(msg.from_user.id, None)
            return

        percent = await update_ref_level(msg.from_user.id)

        await msg.answer(
            f"🎉 Реферал засчитан\n💰 Скидка: {percent}%"
        )

        pending_ref_state.pop(msg.from_user.id, None)
        return


    # ================= ADMIN ADD CODES =================
    if msg.from_user.id in pending:

        data = pending[msg.from_user.id]

        # STEP 1: USER ID
        if data == "wait_user":
            pending[msg.from_user.id] = {
                "step": "wait_amount",
                "user_id": int(msg.text)
            }

            await msg.answer("➕ Сколько рефералов выдать?")
            return

        # STEP 2: AMOUNT
        if isinstance(data, dict) and data.get("step") == "wait_amount":

            user_id = data["user_id"]
            amount = int(msg.text)

            await add_invites(user_id, amount)

            percent = await update_ref_level(user_id)

            pending.pop(msg.from_user.id, None)

            await msg.answer(
                f"✅ Выдано {amount} рефералов\n"
                f"👤 User: {user_id}\n"
                f"💰 Скидка: {percent}%"
            )

            return


# ================= ADMIN PANEL =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="➕ Выдать рефералы", callback_data="admin_add_refs")]
    ])

    await msg.answer("👑 ADMIN PANEL", reply_markup=kb)


# ================= ADMIN STATS =================
@router.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):

    text = f"""
📊 STATISTICS

👤 Users: {await users_count()}
📦 Codes: {await codes_count()}
"""

    await cb.message.answer(text)


# ================= ADMIN ADD REF =================
@router.callback_query(F.data == "admin_add_refs")
async def admin_add_refs(cb: CallbackQuery):

    pending[cb.from_user.id] = "wait_user"

    await cb.message.answer("👤 Введите ID пользователя:")


# ================= DELETE CODE =================
@router.callback_query(F.data.startswith("del_code:"))
async def delete_code(cb: CallbackQuery):

    code = cb.data.split(":")[1]

    await delete_code_db(code)

    await cb.message.answer(f"🗑 Код {code} удалён")
