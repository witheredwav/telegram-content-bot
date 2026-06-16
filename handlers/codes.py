from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import UserStates
from database import get_code, increase_code_usage
from keyboards import user_keyboard

router = Router()

# Кнопка "Ввести код"

@router.callback_query(F.data == "enter_code")
async def enter_code(callback: CallbackQuery, state: FSMContext):

```
await state.set_state(UserStates.waiting_for_code)

await callback.message.answer("🔑 Введите 5-значный код:")

await callback.answer()
```

# Обработка введённого кода

@router.message(UserStates.waiting_for_code)
async def check_code(message: Message, state: FSMContext):

```
code = message.text.strip()

# проверка формата
if not code.isdigit() or len(code) != 5:
    await message.answer("❌ Код должен состоять из 5 цифр.")
    return

# поиск в базе
result = await get_code(code)

if not result:
    await message.answer("❌ Неверный код")
    return

# увеличиваем статистику использования
await increase_code_usage(code)

content_type = result[2]
content = result[3]

# выдача контента
if content_type == "text":
    await message.answer(content)

elif content_type == "photo":
    await message.answer_photo(content)

elif content_type == "document":
    await message.answer_document(content)

elif content_type == "video":
    await message.answer_video(content)

elif content_type == "link":
    await message.answer(f"🔗 {content}")

else:
    await message.answer("❌ Неизвестный тип контента")

# сбрасываем состояние
await state.clear()
```
