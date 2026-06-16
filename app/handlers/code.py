from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from app.database.session import async_session
from app.services.promo_service import PromoService

router = Router()

service = PromoService()


@router.callback_query(F.data == "enter_code")
async def enter_code(callback: CallbackQuery):

    await callback.message.answer(
        "🎁 Введи свой код в следующем сообщении:"
    )

    await callback.answer()


@router.message()
async def process_code(message: Message):

    code = message.text.strip()

    async with async_session() as session:

        promo, text = await service.use_code(session, code)

        if not promo:
            await message.answer(text)
            return

    # выдача контента
    await message.answer(
        f"{text}\n\n"
        f"📦 Контент:\n{promo.content}"
    )
