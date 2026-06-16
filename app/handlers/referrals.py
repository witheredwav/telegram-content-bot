app/handlers/referrals.pyfrom aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.user_service import UserService

router = Router()

user_service = UserService()


@router.callback_query(F.data == "referrals")
async def referrals_handler(callback: CallbackQuery):

    async with async_session() as session:

        user = await user_service.get_or_create_user(
            session=session,
            tg_user=callback.from_user
        )

    await callback.message.answer(
        "👥 Твоя реферальная статистика:\n\n"
        f"🔑 Код: {user.referral_code}\n"
        f"👤 Рефералов: {user.referrals_count}\n"
        f"💰 Скидка: {user.discount_percent}%\n\n"
        f"🔗 Ссылка:\n"
        f"https://t.me/{callback.bot.username}?start={user.referral_code}"
    )

    await callback.answer()
