import random
import string
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *
from keyboards import start_kb, menu_kb, admin_kb

router = Router()

cooldown = {}
pending = {}


# ================= ANTI SPAM =================
def anti_spam(user_id):
    now = datetime.now()
    if user_id in cooldown:
        if now - cooldown[user_id] < timedelta(seconds=2):
            return False
    cooldown[user_id] = now
    return True


# ================= REF CODE =================
def gen_ref():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(9))


# ================= START =================
@router.message(F.text.startswith("/start"))
async def start(msg: Message):

    if not anti_spam(msg.from_user.id):
        return

    await add_user(msg.from_user.id)
    await add_stat("start")

    args = msg.text.split()

    if len(args) > 1:
        await save_pending_ref(msg.from_user.id, args[1])

    await msg.answer("👋 Добро пожаловать!", reply_markup=start_kb())


# ================= CHECK SUB =================
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

    if not anti_spam(cb.from_user.id):
        return

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

    # ================= REF ANTI FRAUD =================
    pending_ref = await get_pending_ref(cb.from_user.id)

    if pending_ref:

        code = pending_ref[0]

        owner = await get_ref_owner(code)

        if owner == cb.from_user.id:
            await clear_pending_ref(cb.from_user.id)
            await cb.message.answer("⚠️ Самореферал запрещён")
            return

        if await ref_exists(cb.from_user.id):
            await clear_pending_ref(cb.from_user.id)
            await cb.message.answer("⚠️ Уже засчитано")
            return

        await add_invite(code)
        await save_ref_log(cb.from_user.id, code)
        await clear_pending_ref(cb.from_user.id)

    await cb.message.answer("✅ Подписка подтверждена", reply_markup=menu_kb())
    await cb.answer()


# ================= CODE =================
@router.callback_query(F.data == "code")
async def code(cb: CallbackQuery):

    if not anti_spam(cb.from_user.id):
        return

    await add_stat("code_open")
    await cb.message.answer("🔑 Введи код")
    await cb.answer()


@router.message(F.text.regexp(r"^\d{5}$"))
async def enter_code(msg: Message):

    if not anti_spam(msg.from_user.id):
        return

    await add_stat("code_enter")

    data = await get_code(msg.text)

    if not data:
        await add_stat("wrong")
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(data[1])


# ================= REF =================
@router.callback_query(F.data == "ref")
async def ref(cb: CallbackQuery):

    data = await get_ref(cb.from_user.id)

    if not data:
        code = gen_ref()
        await create_ref(cb.from_user.id, code)
        data = (code, 0)

    await cb.message.answer(
        f"""👥 РЕФЕРАЛКА

🔑 Код: {data[0]}
👥 Приглашено: {data[1]}

🎁 5 друзей = 20% скидка
"""
    )


# ================= ADMIN =================
@router.message(F.text == "/admin")
async def admin(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("👑 ADMIN", reply_markup=admin_kb())


# ================= STATS =================
@router.callback_query(F.data == "stats")
async def stats(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    await cb.message.answer(f"""
📊 STATS

Users: {await users_count()}
Codes: {await codes_count()}

start: {await get_stat("start")}
check: {await get_stat("check")}
code_enter: {await get_stat("code_enter")}
wrong: {await get_stat("wrong")}
""")
