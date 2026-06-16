from aiogram import Router
from aiogram.types import Message

from app.database.session import async_session
from app.services.user_service import UserService

router = Router()
service = UserService()


@router.message()
async def start_handler(message: Message):

    async with async_session() as session:

        user = await service.get_or_create_user(
            session=session,
            tg_user=message.from_user
        )

    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Твой реферальный код: <b>{user.referral_code}</b>"
    )
