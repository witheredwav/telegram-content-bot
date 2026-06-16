import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *

router = Router()

pending = {}
ref_state = {}
last_action = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):

    await add_user(msg.from_user.id)
    await add_stat("start")

    await msg.answer(
        "👋 Добро пожаловать"
    )


# ================= REF INPUT =================
@router.message()
async def messages(msg: Message):

    uid = msg.from_user.id

    # ================= ANTI SPAM =================
    now = time.time()
    if uid in last_action:
        if now - last_action[uid] < 3:
            await fraud(uid, "spam")
            return

    last_action[uid] = now


    # ================= REF FLOW =================
    if ref_state.get(uid):

        code = msg.text.strip()

        ok = await set_ref(uid, code)

        if not ok:
            await msg.answer("❌ Ошибка реферала")
            await fraud(uid, "invalid_ref")
            ref_state.pop(uid, None)
            return

        await msg.answer("🎉 Реферал засчитан")
        ref_state.pop(uid, None)
        return


    # ================= ADMIN REF CONTROL =================
    if uid in pending:

        data = pending[uid]

        # ADD
        if data["action"] == "add":
            target = data["user_id"]
            amount = int(msg.text)

            await add_invites(target, amount)

            await msg.answer(f"✅ +{amount} рефералов пользователю {target}")
            pending.pop(uid, None)
            return

        # REMOVE
        if data["action"] == "remove":
            target = data["user_id"]
            amount = int(msg.text)

            await remove_invites(target, amount)

            await msg.answer(f"❌ -{amount} рефералов пользователю {target}")
            pending.pop(uid, None)
            return

        # CREATE CODE
        if data["action"] == "code":
            await add_code(msg.text, "content")
            pending.pop(uid, None)
            await msg.answer("✅ код создан")
            return


# ================= ADMIN =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 ADMIN PANEL")


# ================= ADD REF =================
@router.message(F.text.startswith("/addref"))
async def addref(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    _, uid = msg.text.split()
    pending[msg.from_user.id] = {"action": "add", "user_id": int(uid)}

    await msg.answer("➕ сколько добавить?")


# ================= REMOVE REF =================
@router.message(F.text.startswith("/removeref"))
async def removeref(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    _, uid = msg.text.split()
    pending[msg.from_user.id] = {"action": "remove", "user_id": int(uid)}

    await msg.answer("➖ сколько убрать?")


# ================= REF BUTTON =================
@router.message(F.text == "/ref")
async def ref(msg: Message):

    ref_state[msg.from_user.id] = True
    await msg.answer("👥 Введите реф код")


# ================= CREATE CODE =================
@router.message(F.text == "/createcode")
async def createcode(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    pending[msg.from_user.id] = {"action": "code"}
    await msg.answer("🔑 введите код")


# ================= STATS =================
@router.message(F.text == "/stats")
async def stats(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        f"""
📊 STATS
Start: {await get_stat("start")}
Users: {await users_count()}
"""
    )
