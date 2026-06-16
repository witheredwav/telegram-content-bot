from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.keyboards.main_menu import main_menu_keyboard

router = Router()


@router.callback_query(F.data == "menu")
async def open_menu(callback: CallbackQuery):

    await callback.message.answer(
        "📋 Главное меню:",
        reply_markup=main_menu_keyboard()
    )

    await callback.answer()
