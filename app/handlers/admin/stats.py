from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.admin_service import AdminService
from app.repositories.stats_repository import StatsRepository

from app.keyboards.admin_menu import admin_menu_keyboard

router = Router()

admin_service = AdminService()
stats_repo = StatsRepository()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with async_session() as session:

        users = await stats_repo.get_users_count(session)
        subscribed = await stats_repo.get_subscribed_count(session)
        referrals = await stats_repo.get_referrals_count(session)
        codes_used = await stats_repo.get_codes_used(session)

    await callback.message.answer(
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователи: {users}\n"
        f"✅ Подписаны: {subscribed}\n"
        f"👥 Рефералы: {referrals}\n"
        f"🎁 Использовано кодов: {codes_used}\n"
    )

    await callback.answer()
