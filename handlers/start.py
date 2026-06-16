from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import add_user
from keyboards import start_keyboard

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):

    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )

    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Подпишитесь на канал, чтобы получить доступ.",
        reply_markup=start_keyboard()
    )
