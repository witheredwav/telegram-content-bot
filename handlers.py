import random
import aiosqlite

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID, CHANNEL_USERNAME
from db import *
from keyboards import start_kb, menu_kb, admin_kb

router = Router()

pending = {}
pending_delete = {}
pending_ref_delete = {}
pending_ref_code = {}


# ================= START =================
@router.message(F.text.startswith("/start"))
async def start(msg: Message):

    await add_user(msg.from_user.id)
    await add_stat("start")

    await add_event(msg.from_user.id, "start")

    await msg.answer("👋 Добро пожаловать", reply_markup=start_kb())


# ================= CHECK SUB =================
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

    await add_stat("check")
    await add_event(cb.from_user.id, "check")

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


# ================= PORTFOLIO CLICK =================
@router.callback_query(F.data == "portfolio")
async def portfolio(cb: CallbackQuery):
    await add_event(cb.from_user.id, "portfolio")
    await cb.message.answer("📂 Примеры работ...")


# ================= CODE SYSTEM =================
@router.callback_query(F.data == "code")
async def code(cb: CallbackQuery):
    await cb.message.answer("🔑 Введите 5-значный код")


@router.message(F.text.regexp(r"^\d{5}$"))
async def enter_code(msg: Message):

    await add_stat("code")
    await add_event(msg.from_user.id, f"code:{msg.text}")

    data = await get_code(msg.text)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(f"📦 Контент:\n\n{data[1]}")


# ================= ADMIN =================
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer("👑 SAAS PANEL", reply_markup=admin_kb())


# ================= STATS =================
@router.callback_query(F.data == "admin_stats")
async def stats(cb: CallbackQuery):

    top_refs = await top_events("ref_open")
    top_codes = await top_events("start")
    top_portfolio = await top_events("portfolio")

    text = f"""
📊 SAAS ANALYTICS

👤 Users: {await users_count()}
📦 Codes: {await codes_count()}

🔥 TOP REF CLICKS:
{top_refs[:5]}

📂 PORTFOLIO CLICKS:
{top_portfolio[:5]}
"""

    await cb.message.answer(text)


# ================= CODES LIST =================
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
        "📦 КОДЫ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


# ================= DELETE CODE CONFIRM =================
@router.callback_query(F.data.startswith("del_code:"))
async def ask_delete(cb: CallbackQuery):

    code = cb.data.split(":")[1]
    pending_delete[cb.from_user.id] = code

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Удалить", callback_data="confirm_del"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_del")
        ]
    ])

    await cb.message.answer(f"⚠️ Удалить код {code}?", reply_markup=kb)


@router.callback_query(F.data == "confirm_del")
async def confirm_delete(cb: CallbackQuery):

    code = pending_delete.get(cb.from_user.id)

    if not code:
        await cb.message.answer("❌ Нет кода")
        return

    await delete_code_db(code)
    pending_delete.pop(cb.from_user.id, None)

    await cb.message.answer(f"🗑 Код удалён")


@router.callback_query(F.data == "cancel_del")
async def cancel_delete(cb: CallbackQuery):

    pending_delete.pop(cb.from_user.id, None)
    await cb.message.answer("❌ Отменено")


# ================= REF SYSTEM =================
@router.callback_query(F.data == "ref")
async def ref(cb: CallbackQuery):

    await add_event(cb.from_user.id, "ref_open")

    await cb.message.answer("👥 Введите ваш реф код:")
    pending_ref_code[cb.from_user.id] = True


@router.message()
async def ref_enter(msg: Message):

    if msg.from_user.id in pending_ref_code:

        code = msg.text.strip()

        ok = await add_ref_if_valid(msg.from_user.id, code)

        if not ok:
            await msg.answer("⚠️ Реферал не засчитан")
            pending_ref_code.pop(msg.from_user.id)
            return

        percent = await update_ref_level(msg.from_user.id)

        await msg.answer(f"🎉 Реферал засчитан\n💰 Скидка: {percent}%")

        if percent in [10, 15, 20]:
            await msg.answer(f"🏆 Новый уровень скидки: {percent}%")

        pending_ref_code.pop(msg.from_user.id)
        return

    # CREATE CODE SAVE (ADMIN)
    if msg.from_user.id in pending:
        code = pending[msg.from_user.id]

        await add_code(code, msg.text)

        pending.pop(msg.from_user.id)

        await msg.answer("✅ Сохранено")


# ================= REF ADMIN =================
@router.callback_query(F.data == "admin_refs")
async def refs(cb: CallbackQuery):

    data = await get_all_refs()

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


@router.callback_query(F.data.startswith("ref_del:"))
async def ref_del(cb: CallbackQuery):

    user_id = int(cb.data.split(":")[1])
    pending_ref_delete[cb.from_user.id] = user_id

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Удалить", callback_data="confirm_ref_del"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_ref_del")
        ]
    ])

    await cb.message.answer(
        f"⚠️ Удалить реферала {user_id}?",
        reply_markup=kb
    )


@router.callback_query(F.data == "confirm_ref_del")
async def confirm_ref_del(cb: CallbackQuery):

    user_id = pending_ref_delete.get(cb.from_user.id)

    if not user_id:
        await cb.message.answer("❌ Нет данных")
        return

    await delete_ref(user_id)
    pending_ref_delete.pop(cb.from_user.id, None)

    await cb.message.answer("🗑 Удалено")


@router.callback_query(F.data == "cancel_ref_del")
async def cancel_ref_del(cb: CallbackQuery):

    pending_ref_delete.pop(cb.from_user.id, None)
    await cb.message.answer("❌ Отменено")
