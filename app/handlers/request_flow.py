from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.database.session import async_session
from app.services.request_service import RequestService
from app.bot import bot
from app.utils.config import settings

router = Router()

service = RequestService()


class RequestStates(StatesGroup):
    waiting_text = State()


# выбор типа заявки
@router.callback_query(F.data == "request")
async def choose_request_type(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        "📩 Выбери тип заявки:\n\n"
        "1️⃣ Сведение\n"
        "2️⃣ Мастеринг\n"
        "3️⃣ Консультация\n\n"
        "Напиши номер (1-3):"
    )

    await state.set_state(RequestStates.waiting_text)
    await callback.answer()


# обработка типа + текст заявки
@router.message(RequestStates.waiting_text)
async def process_request(message: Message, state: FSMContext):

    mapping = {
        "1": "mixing",
        "2": "mastering",
        "3": "consultation"
    }

    request_type = mapping.get(message.text.strip(), "unknown")

    await state.update_data(request_type=request_type)

    await message.answer("✍️ Теперь опиши свою задачу подробно:")

    await state.set_state(RequestStates.waiting_text)


# финальное сохранение
@router.message(RequestStates.waiting_text)
async def save_request(message: Message, state: FSMContext):

    data = await state.get_data()

    async with async_session() as session:

        req = await service.create_request(
            session=session,
            user_id=message.from_user.id,
            request_type=data.get("request_type"),
            text=message.text
        )

    # уведомление админу
    await bot.send_message(
        settings.ADMIN_IDS.split(",")[0],
        f"📩 Новая заявка!\n\n"
        f"Тип: {req.request_type}\n"
        f"Текст: {req.text}"
    )

    await message.answer(
        "✅ Заявка отправлена!\nЯ свяжусь с тобой в ближайшее время 🎧"
    )

    await state.clear()
