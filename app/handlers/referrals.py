from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text == "Рефералы")
async def referrals_handler(message: Message):
    await message.answer(
        "👥 Реферальная система\n\n"
        "Здесь будет твоя статистика рефералов.\n"
        "Функция пока подключается к базе."
    )
