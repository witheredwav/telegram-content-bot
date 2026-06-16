import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from database import add_code, get_users_count, get_codes_count, get_stats_count
from states import AdminStates

router = Router()

# временное хранение кода (простая версия без сложной логики)

pending_code = {}

# /admin

@router.message(F.text == "/admin")
async def admin_panel(message: Message):

```
if message.from_user.id != ADMIN_ID:
    return await message.answer("❌ Нет доступа")

await message.answer(
    "👑 Админ панель\n\n"
    "/create_code - создать код\n"
    "/stats - статистика"
)
```

# СТАТИСТИКА

@router.message(F.text == "/stats")
async def stats(message: Message):

```
if message.from_user.id != ADMIN_ID:
    return

users = await get_users_count()
codes = await get_codes_count()
actions = await get_stats_count()

await message.answer(
    f"📊 СТАТИСТИКА\n\n"
    f"👤 Пользователей: {users}\n"
    f"🎫 Кодов: {codes}\n"
    f"📈 Действий: {actions}"
)
```

# СОЗДАНИЕ КОДА

@router.message(F.text == "/create_code")
async def create_code(message: Message, state: FSMContext):

```
if message.from_user.id != ADMIN_ID:
    return

code = str(random.randint(0, 99999)).zfill(5)

pending_code[message.from_user.id] = code

await state.set_state(AdminStates.waiting_for_content)

await message.answer(
    f"🎲 Код создан: {code}\n\n"
    "Теперь отправь:\n"
    "📄 текст\n"
    "🖼 фото\n"
    "📁 файл\n"
    "🎥 видео\n"
    "🔗 ссылку"
)
```

# ПОЛУЧЕНИЕ КОНТЕНТА ОТ АДМИНА

@router.message(AdminStates.waiting_for_content)
async def get_content(message: Message, state: FSMContext):

```
if message.from_user.id != ADMIN_ID:
    return

code = pending_code.get(message.from_user.id)

if not code:
    await message.answer("❌ Код не найден")
    return

content_type = None
content = None

if message.text:
    content_type = "text"
    content = message.text

elif message.photo:
    content_type = "photo"
    content = message.photo[-1].file_id

elif message.document:
    content_type = "document"
    content = message.document.file_id

elif message.video:
    content_type = "video"
    content = message.video.file_id

elif message.text and message.text.startswith("http"):
    content_type = "link"
    content = message.text

else:
    await message.answer("❌ Неизвестный формат")
    return

await add_code(code, content_type, content)

pending_code.pop(message.from_user.id)

await state.clear()

await message.answer(f"✅ Код {code} сохранён!")
```
