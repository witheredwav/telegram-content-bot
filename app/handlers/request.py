from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == "request")
async def request_handler(callback: CallbackQuery):

    await callback.message.answer(
        "📩 Оставь заявку прямо сейчас:\n\n"
        "Напиши в одном сообщении:\n"
        "• Что тебе нужно (сведение / мастеринг)\n"
        "• Ссылку на трек\n"
        "• Бюджет\n\n"
        "Я отвечу тебе лично 🎧"
    )

    await callback.answer()
