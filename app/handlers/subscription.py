from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.subscription_service import SubscriptionService
from app.keyboards.subscription import subscription_keyboard

from app.bot import bot

router = Router()

service = SubscriptionService()


@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):

    user_id = callback.from_user.id

    is_sub = await service.is_subscribed(bot, user_id)

    if not is_sub:
        await callback.message.answer(
            "❌ Ты ещё не подписан на канал.",
            reply_markup=subscription_keyboard()
        )
        await callback.answer()
        return

    await callback.message.answer(
        "✅ Подписка подтверждена!\nТеперь тебе открыт доступ к боту 🚀"
    )

    await callback.answer()
