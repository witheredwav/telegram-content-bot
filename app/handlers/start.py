from aiogram import Router
from aiogram.types import Message

from app.database.session import async_session

from app.services.user_service import UserService
from app.services.referral_service import ReferralService
from app.services.subscription_service import SubscriptionService

from app.keyboards.subscription import subscription_keyboard
from app.keyboards.main_menu import main_menu_keyboard

from app.bot import bot

router = Router()

user_service = UserService()
referral_service = ReferralService()
subscription_service = SubscriptionService()


@router.message()
async def start_handler(message: Message):

    args = message.text.split()
    referral_code = args[1] if len(args) > 1 else None

    async with async_session() as session:

        user = await user_service.get_or_create_user(
            session=session,
            tg_user=message.from_user
        )

        await referral_service.process_referral(
            session=session,
            new_user=user,
            referral_code=referral_code
        )

    is_sub = await subscription_service.is_subscribed(
        bot,
        message.from_user.id
    )

    if not is_sub:
        await message.answer(
            "👋 Привет!\n\nПодпишись на канал 👇",
            reply_markup=subscription_keyboard()
        )
        return

    await message.answer(
        "📋 Добро пожаловать в меню!",
        reply_markup=main_menu_keyboard()
    )
