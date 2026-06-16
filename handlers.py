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
pending_admin = {}
pending_ref = {}


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
        pending_ref[msg.from_user.id] = args[1]

    await msg.answer("👋 Добро пожаловать", reply_markup=start_kb())


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

    # ================= REF LOGIC =================
    ref_code = pending_ref.get(cb.from_user.id)

    if ref_code:

        owner = await get_ref_owner(ref_code)

        if owner == cb.from_user.id:
            await cb.message.answer("⚠️ Самореферал")
        else:
            if not await ref_exists(cb.from_user.id):
                await add_invite(ref_code)
                await save_ref_log(cb.from_user.id, ref_code)

        pending_ref.pop(cb.from_user.id)

    await cb.message.answer("✅ OK", reply_markup=menu_kb())
    await cb.answer()


# ================= REF =================
@router.callback_query(F.data == "ref")
async def ref(cb: CallbackQuery):

    data = await get_ref(cb.from_user.id)

    if not data:
        code = gen_ref()
        await create_ref(cb.from_user.id, code)
        data = (code, 0)

    inv = data[1]

    if inv >= 20:
        discount = 20
    elif inv >= 10:
        discount = 15
    elif inv >= 5:
        discount = 10
    else:
        discount = 0

    await cb.message.answer(
        f"""👥 REF SYSTEM

🔑 Code: {data[0]}
👥 Invites: {inv}

🎁 Discount: {discount}%
"""
    )


# ================= CODE =================
@router.callback_query(F.data == "code")
async def code(cb: CallbackQuery):
    await cb.message.answer("🔑 Введи код")


@router.message(F.text.regexp(r"^\d{5}$"))
async def enter_code(msg: Message):

    await add_stat("code")

    data = await get_code(msg.text)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(data[1])


# ================= ADMIN =================
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

    await cb.message.answer(f"""
📊 STATS

Users: {await users_count()}
Codes: {await codes_count()}
start: {await get_stat("start")}
check: {await get_stat("check")}
code: {await get_stat("code")}
""")


# ================= CODES =================
@router.callback_query(F.data == "admin_codes")
async def codes(cb: CallbackQuery):

    if cb.from_user.id != ADMIN_ID:
        return

    data = await get_all_codes()

    if not data:
        await cb.message.answer("❌ Нет кодов")
        return

    text = "\n".join([i[0] for i in data])

    await cb.message.answer(f"📦 CODES:\n\n{text}")


# ================= CREATE CODE =================
@router.callback_query(F.data == "admin_create")
async def create(cb: CallbackQuery):

    code = str(random.randint(10000, 99999))
    pending_admin[cb.from_user.id] = code

    await cb.message.answer(f"🎲 Код: {code}\nОтправь текст")


@router.message()
async def save(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = pending_admin.get(msg.from_user.id)
    if not code:
        return

    await add_code(code, msg.text)
    pending_admin.pop(msg.from_user.id)

    await msg.answer("✅ Сохранено")


# ================= DELETE CODE =================
@router.callback_query(F.data == "admin_delete")
async def delete(cb: CallbackQuery):

    await cb.message.answer("🗑 Отправь код")


@router.message(F.text.regexp(r"^\d{5}$"))
async def delete_code(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await delete_code(msg.text)
    await msg.answer("🗑 Удалено")


# ================= REFS =================
@router.callback_query(F.data == "admin_refs")
async def refs(cb: CallbackQuery):

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM referrals")
        data = await cur.fetchall()

    text = "\n".join([str(i) for i in data])

    await cb.message.answer(f"👥 REFS:\n\n{text}")
