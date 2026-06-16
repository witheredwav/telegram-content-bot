import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F

from aiogram.filters import Command
from aiogram.filters import CommandStart

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import TOKEN
from config import CHANNEL_ID
from config import ADMINS

from database import *

bot = Bot(TOKEN)

dp = Dispatcher()

waiting_for_content = {}


async def is_subscribed(user_id):

    try:

        member = await bot.get_chat_member(
            CHANNEL_ID,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False


def subscribe_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Подписаться",
                    url=f"https://t.me/{CHANNEL_ID.replace('@','')}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Проверить подписку",
                    callback_data="check_sub"
                )
            ]
        ]
    )


@dp.message(CommandStart())
async def start(message: Message):

    if not await is_subscribed(message.from_user.id):

        await message.answer(
            "Для получения контента подпишитесь на канал",
            reply_markup=subscribe_keyboard()
        )

        return

    await show_content_menu(message)


async def show_content_menu(message):

    items = await get_all_content()

    if not items:

        await message.answer(
            "Контент пока отсутствует"
        )

        return

    kb = []

    for item in items:

        kb.append([
            InlineKeyboardButton(
                text=item[1],
                callback_data=f"content_{item[0]}"
            )
        ])

    await message.answer(
        "Выберите контент:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    )


@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):

    if await is_subscribed(callback.from_user.id):

        await callback.message.answer(
            "Подписка подтверждена"
        )

        await show_content_menu(
            callback.message
        )

    else:

        await callback.answer(
            "Вы еще не подписались",
            show_alert=True
        )


@dp.callback_query(F.data.startswith("content_"))
async def open_content(callback: CallbackQuery):

    content_id = int(
        callback.data.split("_")[1]
    )

    item = await get_content(content_id)

    if item:

        await callback.message.answer(
            f"<b>{item[1]}</b>\n\n{item[2]}",
            parse_mode="HTML"
        )


@dp.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id not in ADMINS:
        return

    await message.answer(
        """
Админ-панель

/add - добавить контент
/list - список
/delete ID - удалить
"""
    )


@dp.message(Command("add"))
async def add_start(message: Message):

    if message.from_user.id not in ADMINS:
        return

    waiting_for_content[
        message.from_user.id
    ] = True

    await message.answer(
        "Отправьте:\n\nНазвание|Текст"
    )


@dp.message()
async def add_content_handler(message: Message):

    if message.from_user.id not in ADMINS:
        return

    if message.from_user.id not in waiting_for_content:
        return

    try:

        title, text = message.text.split(
            "|",
            maxsplit=1
        )

        await add_content(
            title.strip(),
            text.strip()
        )

        waiting_for_content.pop(
            message.from_user.id
        )

        await message.answer(
            "Контент добавлен"
        )

    except:

        await message.answer(
            "Формат:\nНазвание|Текст"
        )


@dp.message(Command("list"))
async def list_content(message: Message):

    if message.from_user.id not in ADMINS:
        return

    items = await get_all_content()

    if not items:

        await message.answer(
            "Пусто"
        )

        return

    text = ""

    for item in items:

        text += f"{item[0]} | {item[1]}\n"

    await message.answer(text)


@dp.message(Command("delete"))
async def delete_content_cmd(message: Message):

    if message.from_user.id not in ADMINS:
        return

    parts = message.text.split()

    if len(parts) != 2:
        return

    content_id = int(parts[1])

    await delete_content(content_id)

    await message.answer(
        "Удалено"
    )


async def main():

    await init_db()

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
