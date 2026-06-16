import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *
from keyboards import start_kb, main_kb, ref_kb, admin_kb

router = Router()

waiting = {}
cooldown = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):

    await add_user(msg.from_user.id)

    await msg.answer(
        "👋 Привет",
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
        await cb.message.answer("❌ Не подписан")
        return

    await cb.message.answer("✅ Доступ открыт", reply_markup=main_kb())


# ================= REF MENU =================
@router.callback_query(F.data == "ref_menu")
async def ref_menu(cb: CallbackQuery):

    ref = await get_ref(cb.from_user.id)
    has_code = bool(ref)

    text = f"👥 Ваш код: {ref[0]}\n📊 Рефералы: {ref[1]}" if ref else "👥 У вас нет кода"

    await cb.message.answer(text, reply_markup=ref_kb(has_code))


# ================= CREATE REF =================
@router.callback_query(F.data == "create_ref")
async def create_ref(cb: CallbackQuery):

    code = await create_ref(cb.from_user.id)

    await cb.message.answer(f"🎉 Ваш код: {code}")


# ================= ENTER REF =================
@router.callback_query(F.data == "enter_ref")
async def enter_ref(cb: CallbackQuery):

    waiting[cb.from_user.id] = True
    await cb.message.answer("🔑 Введите реф код")


# ================= REF INPUT =================
@router.message()
async def ref_input(msg: Message):

    uid = msg.from_user.id

    if not waiting.get(uid):
        return

    # cooldown anti spam
    now = time.time()
    if uid in cooldown and now - cooldown[uid] < 3:
        return

    cooldown[uid] = now

    ok = await set_ref(uid, msg.text.strip())

    if ok:
        await msg.answer("🎉 Реф засчитан")
    else:
        await msg.answer("❌ Ошибка")

    waiting.pop(uid, None)


# ================= ADMIN =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 ADMIN", reply_markup=admin_kb())
