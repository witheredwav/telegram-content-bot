from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.admin_service import AdminService
from app.services.analytics_service import AnalyticsService

router = Router()

admin_service = AdminService()
analytics = AnalyticsService()


@router.callback_query(F.data == "admin_analytics")
async def analytics_handler(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with async_session() as session:

        data = await analytics.get_full_stats(session)

    text = (
        "📊 <b>Аналитика продаж</b>\n\n"
        f"👥 Пользователи: {data['users']}\n"
        f"👥 Рефералы: {data['referrals']}\n"
        f"📩 Заявки: {data['requests']}\n"
        f"💰 Заказы: {data['orders']}\n"
        f"💵 Доход: {data['income']}₽\n"
        f"📈 Конверсия: {data['conversion']}%\n"
    )

    await callback.message.answer(text)

    await callback.answer()
