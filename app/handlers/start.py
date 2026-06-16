from aiogram import Router
from aiogram.types import Message

from app.database.session import async_session

from app.services.user_service import UserService
from app.services.referral_service import ReferralService

router = Router()

user_service = UserService()
referral_service = ReferralService()


@router.message()
async def start_handler(message: Message):

    # пробуем взять реф код из /start ABC123
    args = message.text.split()

    referral_code = None

    if len(args) > 1:
        referral_code = args[1]

    async with async_session() as session:

        # 1. создаём / получаем пользователя
        user = await user_service.get_or_create_user(
            session=session,
            tg_user=message.from_user
        )

        # 2. применяем реферальную систему
        await referral_service.process_referral(
            session=session,
            new_user=user,
            referral_code=referral_code
        )

    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        f"🎁 Твой реферальный код: <b>{user.referral_code}</b>\n"
        f"👥 Рефералов: {user.referrals_count}\n"
        f"💰 Скидка: {user.discount_percent}%"
    )
