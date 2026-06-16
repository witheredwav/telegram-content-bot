from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.admin_service import AdminService
from app.services.order_service import OrderService

router = Router()

admin_service = AdminService()
order_service = OrderService()


# 📋 список заказов
@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with async_session() as session:

        orders = await order_service.get_orders(session)

    if not orders:
        await callback.message.answer("📭 Заказов нет")
        return

    text = "📋 <b>Заказы клиентов</b>\n\n"

    for o in orders[:10]:
        text += (
            f"🆔 {o.id}\n"
            f"👤 user: {o.user_id}\n"
            f"📌 {o.request_type}\n"
            f"💰 {o.amount}₽\n"
            f"📊 {o.status}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()


# 💰 отметить как оплачено
@router.callback_query(F.data.startswith("order_paid_"))
async def mark_paid(callback: CallbackQuery):

    order_id = int(callback.data.split("_")[-1])

    async with async_session() as session:

        await order_service.mark_as_paid(session, order_id)

    await callback.message.answer(f"💰 Заказ {order_id} отмечен как ОПЛАЧЕН")

    await callback.answer()
