import random
from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


def generate_code():
    return str(random.randint(10000, 99999))


@router.callback_query(F.data == "admin_create_code")
async def create_code(callback: CallbackQuery):

    code = generate_code()

    await callback.message.answer(
        "🎁 Новый код создан:\n\n"
        f"<b>{code}</b>\n\n"
        "⚙️ Сейчас это тестовая версия.\n"
        "Дальше добавим привязку файлов и лимиты."
    )

    await callback.answer()
