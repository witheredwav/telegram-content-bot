import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    ReplyKeyboardRemove
)

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")          # например: @mychannel или -1001234567890
CHANNEL_LINK = os.getenv("CHANNEL_LINK")      # https://t.me/mychannel
WORKS_CHANNEL_LINK = os.getenv("WORKS_CHANNEL_LINK")  # https://t.me/myworks
DM_LINK = os.getenv("DM_LINK")               # https://t.me/myusername

DB_FILE = "db.json"

# ─── БД (простой JSON) ────────────────────────────────────────────────────────

def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        return {"codes": {}, "stats": {"total": {}, "daily": {}}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def track_click(event: str):
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    db["stats"]["total"][event] = db["stats"]["total"].get(event, 0) + 1
    if today not in db["stats"]["daily"]:
        db["stats"]["daily"][today] = {}
    db["stats"]["daily"][today][event] = db["stats"]["daily"][today].get(event, 0) + 1
    save_db(db)

def get_stats() -> str:
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    total = db["stats"].get("total", {})
    daily = db["stats"].get("daily", {}).get(today, {})

    events = ["start", "subscribe", "check_sub", "works", "order", "enter_key"]
    labels = {
        "start": "/start", "subscribe": "Подписаться",
        "check_sub": "Проверить подписку", "works": "Примеры работ",
        "order": "Заказать сведение", "enter_key": "Ввести ключ"
    }

    lines = ["📊 *Статистика*\n"]
    lines.append("*За сегодня:*")
    for e in events:
        lines.append(f"  {labels[e]}: {daily.get(e, 0)}")
    lines.append("\n*Всего:*")
    for e in events:
        lines.append(f"  {labels[e]}: {total.get(e, 0)}")
    return "\n".join(lines)

def next_code() -> str:
    db = load_db()
    existing = set(db["codes"].keys())
    for i in range(1, 100000):
        code = f"{i:05d}"
        if code not in existing:
            return code
    return None

# ─── FSM ──────────────────────────────────────────────────────────────────────

class UserState(StatesGroup):
    waiting_key = State()

class AdminState(StatesGroup):
    waiting_content_type = State()
    waiting_content = State()
    confirm_delete = State()

# ─── КЛАВИАТУРЫ ───────────────────────────────────────────────────────────────

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton(text="🎧 Примеры работ", url=WORKS_CHANNEL_LINK)],
        [InlineKeyboardButton(text="💬 Заказать сведение", url=DM_LINK)],
        [InlineKeyboardButton(text="🔑 Ввести ключ", callback_data="enter_key")],
    ])

def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="➕ Создать код", callback_data="admin_create")],
        [InlineKeyboardButton(text="📦 Коды", callback_data="admin_codes")],
    ])

def content_type_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Текст", callback_data="ctype_text"),
         InlineKeyboardButton(text="🖼 Фото", callback_data="ctype_photo")],
        [InlineKeyboardButton(text="🎬 Видео", callback_data="ctype_video"),
         InlineKeyboardButton(text="📁 Файл", callback_data="ctype_file")],
        [InlineKeyboardButton(text="🔗 Ссылка", callback_data="ctype_link")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")],
    ])

def confirm_delete_kb(code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"del_yes_{code}"),
         InlineKeyboardButton(text="❌ Нет", callback_data="admin_codes")],
    ])

def back_to_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")]
    ])

# ─── BOT + DISPATCHER ─────────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ─── /start ───────────────────────────────────────────────────────────────────

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    track_click("start")
    await message.answer(
        "👋 Привет! Я бот для получения файлов по секретным кодам.\n\nВыбери действие:",
        reply_markup=main_menu_kb()
    )

# ─── ПРОВЕРКА ПОДПИСКИ ────────────────────────────────────────────────────────

@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    track_click("check_sub")
    try:
        member = await bot.get_chat_member(CHANNEL_ID, callback.from_user.id)
        if member.status in ("member", "administrator", "creator"):
            await callback.answer("✅ Ты подписан на канал!", show_alert=True)
        else:
            await callback.answer("❌ Ты не подписан. Подпишись сначала!", show_alert=True)
    except Exception:
        await callback.answer("⚠️ Не могу проверить подписку. Убедись, что бот — администратор канала.", show_alert=True)

@dp.callback_query(F.data == "enter_key")
async def enter_key_start(callback: types.CallbackQuery, state: FSMContext):
    track_click("enter_key")
    await state.set_state(UserState.waiting_key)
    await callback.message.answer("🔑 Введи 5-значный код:")
    await callback.answer()

# ─── ВВОД КОДА ────────────────────────────────────────────────────────────────

@dp.message(UserState.waiting_key)
async def process_key(message: types.Message, state: FSMContext):
    code = message.text.strip()
    db = load_db()

    if code not in db["codes"]:
        await message.answer("❌ Неверный код. Попробуй ещё раз или вернись в меню:", reply_markup=main_menu_kb())
        await state.clear()
        return

    entry = db["codes"][code]
    ctype = entry["type"]
    content = entry["content"]
    caption = entry.get("caption", "")

    await state.clear()

    if ctype == "text":
        await message.answer(f"✅ Контент по коду *{code}*:\n\n{content}", parse_mode="Markdown")
    elif ctype == "link":
        await message.answer(f"✅ Ссылка по коду *{code}*:\n{content}", parse_mode="Markdown")
    elif ctype == "photo":
        await message.answer_photo(content, caption=caption or f"Код: {code}")
    elif ctype == "video":
        await message.answer_video(content, caption=caption or f"Код: {code}")
    elif ctype == "file":
        await message.answer_document(content, caption=caption or f"Код: {code}")
    else:
        await message.answer("⚠️ Неизвестный тип контента.")

    await message.answer("Главное меню:", reply_markup=main_menu_kb())

# ─── /admin ───────────────────────────────────────────────────────────────────

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    await state.clear()
    await message.answer("🛠 Админ-панель:", reply_markup=admin_menu_kb())

@dp.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_text("🛠 Админ-панель:", reply_markup=admin_menu_kb())

@dp.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_text("🛠 Админ-панель:", reply_markup=admin_menu_kb())

# ─── СТАТИСТИКА ───────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.edit_text(get_stats(), parse_mode="Markdown", reply_markup=back_to_admin_kb())

# ─── СОЗДАТЬ КОД ──────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "admin_create")
async def admin_create(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    code = next_code()
    if not code:
        await callback.answer("❌ Все коды исчерпаны!", show_alert=True)
        return
    await state.update_data(new_code=code)
    await state.set_state(AdminState.waiting_content_type)
    await callback.message.edit_text(
        f"➕ Новый код: *{code}*\n\nВыбери тип контента:",
        parse_mode="Markdown",
        reply_markup=content_type_kb()
    )

@dp.callback_query(F.data.startswith("ctype_"))
async def admin_content_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    ctype = callback.data.replace("ctype_", "")
    await state.update_data(content_type=ctype)
    await state.set_state(AdminState.waiting_content)

    prompts = {
        "text": "📝 Отправь текст:",
        "photo": "🖼 Отправь фото:",
        "video": "🎬 Отправь видео:",
        "file": "📁 Отправь файл:",
        "link": "🔗 Отправь ссылку:",
    }
    await callback.message.edit_text(prompts.get(ctype, "Отправь контент:"))

@dp.message(AdminState.waiting_content)
async def admin_save_content(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    code = data["new_code"]
    ctype = data["content_type"]

    db = load_db()
    entry = {"type": ctype}

    if ctype == "text":
        entry["content"] = message.text
    elif ctype == "link":
        entry["content"] = message.text
    elif ctype == "photo":
        entry["content"] = message.photo[-1].file_id
        entry["caption"] = message.caption or ""
    elif ctype == "video":
        entry["content"] = message.video.file_id
        entry["caption"] = message.caption or ""
    elif ctype == "file":
        entry["content"] = message.document.file_id
        entry["caption"] = message.caption or ""
    else:
        await message.answer("⚠️ Неизвестный тип.")
        await state.clear()
        return

    db["codes"][code] = entry
    save_db(db)
    await state.clear()

    await message.answer(
        f"✅ Код *{code}* сохранён!\nТип: {ctype}",
        parse_mode="Markdown",
        reply_markup=admin_menu_kb()
    )

# ─── СПИСОК КОДОВ ─────────────────────────────────────────────────────────────

@dp.callback_query(F.data == "admin_codes")
async def admin_codes(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    db = load_db()
    codes = db["codes"]

    if not codes:
        await callback.message.edit_text("📦 Кодов пока нет.", reply_markup=back_to_admin_kb())
        return

    buttons = []
    for code, entry in sorted(codes.items()):
        label = f"{code} ({entry['type']})"
        buttons.append([
            InlineKeyboardButton(text=label, callback_data=f"view_{code}"),
            InlineKeyboardButton(text="❌", callback_data=f"ask_del_{code}")
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")])

    await callback.message.edit_text(
        f"📦 Всего кодов: {len(codes)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("ask_del_"))
async def ask_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    code = callback.data.replace("ask_del_", "")
    await callback.message.edit_text(
        f"🗑 Удалить код *{code}*?",
        parse_mode="Markdown",
        reply_markup=confirm_delete_kb(code)
    )

@dp.callback_query(F.data.startswith("del_yes_"))
async def confirm_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    code = callback.data.replace("del_yes_", "")
    db = load_db()
    if code in db["codes"]:
        del db["codes"][code]
        save_db(db)
        await callback.answer(f"✅ Код {code} удалён.", show_alert=True)
    else:
        await callback.answer("❌ Код не найден.", show_alert=True)

    # Вернуть список
    codes = db["codes"]
    if not codes:
        await callback.message.edit_text("📦 Кодов пока нет.", reply_markup=back_to_admin_kb())
        return

    buttons = []
    for c, entry in sorted(codes.items()):
        label = f"{c} ({entry['type']})"
        buttons.append([
            InlineKeyboardButton(text=label, callback_data=f"view_{c}"),
            InlineKeyboardButton(text="❌", callback_data=f"ask_del_{c}")
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_back")])
    await callback.message.edit_text(
        f"📦 Всего кодов: {len(codes)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
