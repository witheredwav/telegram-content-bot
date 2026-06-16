from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.services.admin_service import AdminService
from app.keyboards.admin_dashboard import admin_dashboard_keyboard

router = Router()

admin_service = AdminService()


@router.callback_query(F.data == "admin")
async def admin_menu(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await callback.message.answer(
        "🛠 <b>Добро пожаловать в админ-панель</b>",
        reply_markup=admin_dashboard_keyboard()
    )

    await callback.answer()
