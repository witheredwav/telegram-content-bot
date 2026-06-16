import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatMemberStatus

from config import CHANNEL_USERNAME, ADMIN_ID
from db import add_user, get_code
from keyboards import start_kb, menu_kb
from states import Code

router = Router()


# START
@router.message(F.text == "/start")
async def start(msg: Message):
    await add_user(msg.from_user.id)

    await msg.answer(
        "Подпишись на канал",
        reply_markup=start_kb()
    )


# CHECK SUB
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

    member = await cb.bot.get_chat_member(
        f"@{CHANNEL_USERNAME}",
        cb.from_user.id
    )

    if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
        await cb.message.answer("Ок", reply_markup=menu_kb())
    else:
        await cb.message.answer("❌ не подписан")

    await cb.answer()


# ENTER CODE
@router.callback_query(F.data == "code")
async def enter(cb: CallbackQuery, state: FSMContext):

    await state.set_state(Code.wait)
    await cb.message.answer("Введи код:")
    await cb.answer()


# CHECK CODE
@router.message(Code.wait)
async def check_code(msg: Message, state: FSMContext):

    code = msg.text.strip()

    if len(code) != 5 or not code.isdigit():
        await msg.answer("❌ 5 цифр")
        return

    data = await get_code(code)

    if not data:
        await msg.answer("❌ Неверный код")
        return

    await msg.answer(f"✅ Доступ: {data[2]}")

    await state.clear()


# ADMIN (простая генерация)
@router.message(F.text == "/admin")
async def admin(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(0, 99999)).zfill(5)

    await msg.answer(f"Код: {code}")
