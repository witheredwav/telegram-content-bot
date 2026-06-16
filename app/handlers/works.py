from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.utils.config import settings

router = Router()


@router.callback_query(F.data == "works")
async def works_handler(callback: CallbackQuery):

    await callback.message.answer(
        "🎧 Примеры моих работ:\n\n"
        f"👉 https://t.me/{settings.WORKS_CHANNEL_USERNAME}\n\n"
        "Там ты найдёшь:\n"
        "• Сведение треков\n"
        "• Мастеринг\n"
        "• Кейсы клиентов\n"
    )

    await callback.answer()
