import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from db import add_code, users_count
from keyboards import start_kb, menu_kb

router = Router()

pending_code = {}


# /start
@router.message(F.text == "/start")
async def start(msg: Message):

    await msg.answer(
        "👋 Привет!\n\nПодпишись на канал",
        reply_markup=start_kb()
    )


# CHECK SUB (заглушка, если у тебя есть — оставь свою)
@router.callback_query(F.data == "check")
async def check(cb: CallbackQuery):

    await cb.message.answer("✅ Проверка (сюда подключим подписку позже)")
    await cb.answer()


# MENU
@router.callback_query(F.data == "code")
async def code_menu(cb: CallbackQuery, state: FSMContext):

    await state.set_state(None)
    await cb.message.answer("🔑 Введите код:")
    await cb.answer()


# =========================
# 👑 АДМИН ПАНЕЛЬ
# =========================

@router.message(F.text == "/admin")
async def admin_panel(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    await msg.answer(
        "👑 АДМИН ПАНЕЛЬ\n\n"
        "/create_code — создать код\n"
        "/stats — статистика"
    )


# СОЗДАНИЕ КОДА
@router.message(F.text == "/create_code")
async def create_code(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(0, 99999)).zfill(5)

    pending_code[msg.from_user.id] = code

    await msg.answer(
        f"🎲 Код создан: {code}\n\n"
        "Теперь отправь:\n"
        "- текст\n"
        "- фото\n"
        "- файл\n"
        "- видео\n"
        "- ссылку"
    )


# ПОЛУЧЕНИЕ КОНТЕНТА ОТ АДМИНА
@router.message()
async def admin_content(msg: Message):

    if msg.from_user.id != ADMIN_ID:
        return

    code = pending_code.get(msg.from_user.id)

    if not code:
        return

    content_type = None
    content = None

    if msg.photo:
        content_type = "photo"
        content = msg.photo[-1].file_id

    elif msg.document:
        content_type = "document"
        content = msg.document.file_id

    elif msg.video:
        content_type = "video"
        content = msg.video.file_id

    elif msg.text:
        content_type = "text"
        content = msg.text

    else:
        await msg.answer("❌ Неизвестный формат")
        return

    await add_code(code, content_type, content)

    pending_code.pop(msg.from_user.id)

    await msg.answer(f"✅ Код {code} сохранён!")
