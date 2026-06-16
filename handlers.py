import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *
from keyboards import start_kb, admin_kb

router = Router()

pending = {}
pending_ref_state = {}
last_action = {}


# ================= START =================
@router.message(F.text.startswith("/start"))
async def start(msg: Message):

    await add_user(msg.from_user.id)
    await add_event(msg.from_user.id, "start")

    await msg.answer(
        "👋 Добро пожаловать в систему\n\n👇 Выберите действие:",
        reply_markup=start_kb()
    )


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


# ================= PORTFOLIO =================
@router.callback_query(F.data == "portfolio")
async def portfolio(cb: CallbackQuery):
    await add_event(cb.from_user.id, "portfolio")
    await cb.message.answer("📂 Примеры работ...")


# ================= CODE INPUT =================
@router.message(F.text.regexp(r"^\d{5}$"))
async def code_input(msg: Message):

    data = await get_code(msg.text)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(f"📦 Контент:\n\n{data[1]}")


# ================= REF BUTTON =================
@router.callback_query(F.data == "ref")
async def ref(cb: CallbackQuery):

    pending_ref_state[cb.from_user.id] = True

    await cb.message.answer("👥 Введите реферальный код:")


# ================= REF INPUT + ANTI SPAM =================
@router.message()
async def all_messages(msg: Message):

    # ================= REF SYSTEM =================
    if pending_ref_state.get(msg.from_user.id):

        now = time.time()

        if msg.from_user.id in last_action:
            if now - last_action[msg.from_user.id] < 3:
                await msg.answer("⛔ Слишком быстро")
                return

        last_action[msg.from_user.id] = now

        code = msg.text.strip()

        ok = await add_ref_if_valid(msg.from_user.id, code)

        if not ok:
            await msg.answer("❌ Реферал не засчитан")
            pending_ref_state.pop(msg.from_user.id, None)
            return

        percent = await update_ref_level(msg.from_user.id)

        await msg.answer(f"🎉 Реферал засчитан\n💰 Скидка: {percent}%")

        pending_ref_state.pop(msg.from_user.id, None)
        return


    # ================= ADMIN REF ADD =================
    if msg.from_user.id in pending:

        data = pending[msg.from_user.id]

        if data == "wait_user":
            pending[msg.from_user.id] = {
                "step": "wait_amount",
                "user_id": int(msg.text)
            }

            await msg.answer("➕ Сколько рефералов выдать?")
            return

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

    await msg.answer("👑 ADMIN PANEL", reply_markup=admin_kb())


# ================= STATS =================
@router.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):

    await cb.message.answer(
        f"📊 STATISTICS\n\n"
        f"👤 Users: {await users_count()}\n"
        f"📦 Codes: {await codes_count()}"
    )


# ================= ADMIN ADD REF =================
@router.callback_query(F.data == "admin_add_refs")
async def admin_add_refs(cb: CallbackQuery):

    pending[cb.from_user.id] = "wait_user"

    await cb.message.answer("👤 Введите ID пользователя:")
