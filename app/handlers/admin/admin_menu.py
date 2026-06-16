from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards.admin_menu import admin_menu_keyboard
from app.services.admin_service import AdminService

router = Router()

admin_service = AdminService()


@router.callback_query(F.data == "admin")
async def admin_menu(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await callback.message.answer(
        "🛠 Админ-панель:",
        reply_markup=admin_menu_keyboard()
    )

    await callback.answer()
