import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *
from keyboards import start_kb, main_kb, admin_kb

router = Router()

ref_wait = {}
last_action = {}


# ================= START =================
@router.message(F.text == "/start")
async def start(msg: Message):

    await add_user(msg.from_user.id)
    await add_stat("start")

    await msg.answer(
        "👋 Привет!\n\nПодпишись и нажми проверить",
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
        await cb.message.answer("❌ Ты не подписан")
        return

    await cb.message.answer("✅ Доступ открыт", reply_markup=main_kb())


# ================= MAIN FEATURES =================
@router.callback_query(F.data == "code")
async def code(cb: CallbackQuery):
    await cb.message.answer("🔑 Введите код:")


@router.message(F.text.regexp(r"^\d{5}$"))
async def code_input(msg: Message):

    data = await get_code(msg.text)

    if not data:
        await msg.answer("❌ Код не найден")
        return

    await msg.answer(f"📦 {data[1]}")


# ================= REF =================
@router.callback_query(F.data == "ref")
async def ref(cb: CallbackQuery):

    me = await my_ref(cb.from_user.id)

    if me:
        await cb.message.answer(
            f"👥 Ваш код: {me[0]}\n📊 Рефералы: {me[1]}"
        )
    else:
        await cb.message.answer("❌ У вас нет реф кода")


@router.message()
async def ref_input(msg: Message):

    uid = msg.from_user.id

    if ref_wait.get(uid):

        now = time.time()

        if uid in last_action and now - last_action[uid] < 3:
            await msg.answer("⛔ Слишком быстро")
            return

        last_action[uid] = now

        ok = await set_ref(uid, msg.text.strip())

        if not ok:
            await msg.answer("❌ Реф не засчитан")
            ref_wait.pop(uid, None)
            return

        await msg.answer("🎉 Реферал засчитан")
        ref_wait.pop(uid, None)
        return


# ================= ADMIN PANEL =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 ADMIN PANEL", reply_markup=admin_kb())


# ================= ADMIN BUTTONS =================
@router.callback_query(F.data == "admin_add_refs")
async def add_refs(cb: CallbackQuery):

    await set_pending(cb.from_user.id, "add_refs")
    await cb.message.answer("👤 Введи ID пользователя")


@router.callback_query(F.data == "admin_remove_refs")
async def remove_refs(cb: CallbackQuery):

    await set_pending(cb.from_user.id, "remove_refs")
    await cb.message.answer("👤 Введи ID пользователя")


@router.callback_query(F.data == "admin_create_code")
async def create_code(cb: CallbackQuery):

    await set_pending(cb.from_user.id, "create_code")
    await cb.message.answer("🔑 Введи код")


# ================= ADMIN INPUT FLOW =================
@router.message()
async def admin_flow(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    pending = await get_pending(msg.from_user.id)

    if not pending:
        return

    action, target = pending

    # ADD REFS
    if action == "add_refs" and not target:
        await set_pending(msg.from_user.id, "add_refs", int(msg.text))
        await msg.answer("➕ Сколько добавить?")
        return

    if action == "add_refs" and target:
        await add_invites(int(msg.text), target)
        await clear_pending(msg.from_user.id)
        await msg.answer("✅ добавлено")
        return

    # REMOVE REFS
    if action == "remove_refs" and not target:
        await set_pending(msg.from_user.id, "remove_refs", int(msg.text))
        await msg.answer("➖ Сколько убрать?")
        return

    if action == "remove_refs" and target:
        await remove_invites(int(msg.text), target)
        await clear_pending(msg.from_user.id)
        await msg.answer("❌ убрано")
        return

    # CREATE CODE
    if action == "create_code":
        await add_code(msg.text, "content")
        await clear_pending(msg.from_user.id)
        await msg.answer("✅ код создан")
        return


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
