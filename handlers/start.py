from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import add_user
from keyboards import start_keyboard

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):


await add_user(
    telegram_id=message.from_user.id,
    username=message.from_user.username,
    first_name=message.from_user.first_name
)

await message.answer(
    "👋 Добро пожаловать!\n\n"
    "Для получения доступа необходимо подписаться на канал.",
    reply_markup=start_keyboard()
)

