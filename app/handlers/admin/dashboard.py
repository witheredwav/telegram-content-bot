from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.services.admin_service import AdminService
from app.keyboards.admin_dashboard import admin_dashboard_keyboard

router = Router()

admin_service = AdminService()


@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await callback.message.answer(
        "🛠 <b>Админ-панель</b>\n\nВыбери раздел:",
        reply_markup=admin_dashboard_keyboard()
    )

    await callback.answer()
