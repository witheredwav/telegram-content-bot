import asyncio
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
logging.basicConfig(level=logging.INFO)

# ─── КОНФИГ ───────────────────────────────────────────────────────────────────

BOT_TOKEN          = os.getenv("BOT_TOKEN")
ADMIN_ID           = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID         = os.getenv("CHANNEL_ID")           # @username или -100...
CHANNEL_LINK       = os.getenv("CHANNEL_LINK")         # https://t.me/...
WORKS_CHANNEL_LINK = os.getenv("WORKS_CHANNEL_LINK")   # https://t.me/...
DM_LINK            = os.getenv("DM_LINK")              # https://t.me/username

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан! Добавь переменную окружения BOT_TOKEN.")

DB_FILE = "db.json"

# ─── БД ───────────────────────────────────────────────────────────────────────

def load_db() -> dict:
    if not os.path.exists(DB_FILE):
        return {"codes": {}, "stats": {"total": {}, "daily": {}}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def track(event: str):
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    db["stats"]["total"][event] = db["stats"]["total"].get(event, 0) + 1
    db["stats"]["daily"].setdefault(today, {})
    db["stats"]["daily"][today][event] = db["stats"]["daily"][today].get(event, 0) + 1
    save_db(db)

def get_stats_text() -> str:
    db = load_db()
    today = datetime.now().strftime("%Y-%m-%d")
    total = db["stats"].get("total", {})
    daily = db["stats"].get("daily", {}).get(today, {})
    events = {
        "start":     "🚀 /start",
        "check_sub": "✅ Проверка подписки",
        "works":     "🎧 Примеры работ",
        "order":     "💬 Заказать сведение",
        "enter_key": "🔑 Ввод ключа",
    }
    lines = ["📊 *Статистика кликов*\n", "*За сегодня:*"]
    for e, label in events.items():
        lines.append(f"  {label}: {daily.get(e, 0)}")
    lines.append("\n*Всего за всё время:*")
    for e, label in events.items():
        lines.append(f"  {label}: {total.get(e, 0)}")
    return "\n".join(lines)

def next_free_code() -> str | None:
    db = load_db()
    existing = set(db["codes"].keys())
    for i in range(1, 100000):
        code = f"{i:05d}"
        if code not in existing:
            return code
    return None

# ─── FSM ──────────────────────────────────────────────────────────────────────

class UserFSM(StatesGroup):
    waiting_key = State()

class AdminFSM(StatesGroup):
    choose_type  = State()
    send_content = State()

# ─── КЛАВИАТУРЫ ───────────────────────────────────────────────────────────────

def kb_page1() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Проверить подписку",   callback_data="check_sub")],
    ])

def kb_page2() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎧 Примеры работ",     url=WORKS_CHANNEL_LINK)],
        [InlineKeyboardButton(text="💬 Заказать сведение",  url=DM_LINK)],
        [InlineKeyboardButton(text="🔑 Ввести ключ",        callback_data="enter_key")],
        [InlineKeyboardButton(text="◀️ Назад",              callback_data="back_to_page1")],
    ])

def kb_cancel_key() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_key")]
    ])

def kb_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика",   callback_data="admin_stats")],
        [InlineKeyboardButton(text="➕ Создать код",  callback_data="admin_create")],
        [InlineKeyboardButton(text="📦 Список кодов", callback_data="admin_codes")],
    ])

def kb_content_type() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Текст", callback_data="ctype_text"),
         InlineKeyboardButton(text="🖼 Фото",  callback_data="ctype_photo")],
        [InlineKeyboardButton(text="🎬 Видео", callback_data="ctype_video"),
         InlineKeyboardButton(text="📁 Файл",  callback_data="ctype_file")],
        [InlineKeyboardButton(text="🔗 Ссылка", callback_data="ctype_link")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_home")],
    ])

def kb_confirm_del(code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"del_yes_{code}"),
         InlineKeyboardButton(text="❌ Отмена",       callback_data="admin_codes")],
    ])

def kb_back_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="admin_home")]
    ])

def kb_cancel_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_home")]
    ])

def build_codes_kb(codes: dict) -> InlineKeyboardMarkup:
    buttons = []
    for code, entry in sorted(codes.items()):
        buttons.append([
            InlineKeyboardButton(text=f"🔑 {code}  [{entry['type']}]", callback_data=f"view_{code}"),
            InlineKeyboardButton(text="🗑",                             callback_data=f"ask_del_{code}"),
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_home")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── BOT ──────────────────────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  ПОЛЬЗОВАТЕЛЬ
# ══════════════════════════════════════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    track("start")
    await message.answer(
        "👋 Привет!\n\n"
        "Чтобы получить доступ к боту — подпишись на наш канал и нажми *«Проверить подписку»*.",
        parse_mode="Markdown",
        reply_markup=kb_page1()
    )

@dp.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: types.CallbackQuery):
    track("check_sub")
    if await is_subscribed(callback.from_user.id):
        await callback.message.edit_text(
            "✅ Подписка подтверждена!\n\nДобро пожаловать. Выбери действие:",
            reply_markup=kb_page2()
        )
    else:
        await callback.answer(
            "❌ Ты ещё не подписан на канал.\nПодпишись и попробуй снова!",
            show_alert=True
        )

@dp.callback_query(F.data == "back_to_page1")
async def cb_back_page1(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "👋 Привет!\n\n"
        "Чтобы получить доступ к боту — подпишись на наш канал и нажми *«Проверить подписку»*.",
        parse_mode="Markdown",
        reply_markup=kb_page1()
    )

@dp.callback_query(F.data == "enter_key")
async def cb_enter_key(callback: types.CallbackQuery, state: FSMContext):
    track("enter_key")
    if not await is_subscribed(callback.from_user.id):
        await callback.answer("❌ Сначала подпишись на канал!", show_alert=True)
        return
    await state.set_state(UserFSM.waiting_key)
    await callback.message.answer("🔑 Введи 5-значный код:", reply_markup=kb_cancel_key())
    await callback.answer()

@dp.callback_query(F.data == "cancel_key")
async def cb_cancel_key(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=kb_page2())

@dp.message(UserFSM.waiting_key)
async def process_key(message: types.Message, state: FSMContext):
    code = message.text.strip() if message.text else ""
    db = load_db()
    if code not in db["codes"]:
        await message.answer("❌ Неверный код. Попробуй ещё раз:", reply_markup=kb_cancel_key())
        return
    entry   = db["codes"][code]
    ctype   = entry["type"]
    content = entry["content"]
    caption = entry.get("caption", "") or f"Код: {code}"
    await state.clear()
    if ctype in ("text", "link"):
        await message.answer(f"✅ *Код {code}:*\n\n{content}", parse_mode="Markdown")
    elif ctype == "photo":
        await message.answer_photo(content, caption=caption)
    elif ctype == "video":
        await message.answer_video(content, caption=caption)
    elif ctype == "file":
        await message.answer_document(content, caption=caption)
    await message.answer("Главное меню:", reply_markup=kb_page2())

# ══════════════════════════════════════════════════════════════════════════════
#  АДМИН
# ══════════════════════════════════════════════════════════════════════════════

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа.")
        return
    await state.clear()
    await message.answer("🛠 *Админ-панель*", parse_mode="Markdown", reply_markup=kb_admin())

@dp.callback_query(F.data == "admin_home")
async def cb_admin_home(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text("🛠 *Админ-панель*", parse_mode="Markdown", reply_markup=kb_admin())

@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await callback.message.edit_text(get_stats_text(), parse_mode="Markdown", reply_markup=kb_back_admin())

@dp.callback_query(F.data == "admin_create")
async def cb_admin_create(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    code = next_free_code()
    if not code:
        await callback.answer("❌ Все коды исчерпаны!", show_alert=True)
        return
    await state.update_data(new_code=code)
    await state.set_state(AdminFSM.choose_type)
    await callback.message.edit_text(
        f"➕ Новый код: *{code}*\n\nВыбери тип контента:",
        parse_mode="Markdown",
        reply_markup=kb_content_type()
    )

@dp.callback_query(F.data.startswith("ctype_"))
async def cb_choose_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    ctype = callback.data.replace("ctype_", "")
    await state.update_data(content_type=ctype)
    await state.set_state(AdminFSM.send_content)
    prompts = {
        "text":  "📝 Отправь текстовое сообщение:",
        "photo": "🖼 Отправь фото (можно с подписью):",
        "video": "🎬 Отправь видео (можно с подписью):",
        "file":  "📁 Отправь файл (можно с подписью):",
        "link":  "🔗 Отправь ссылку текстом:",
    }
    await callback.message.edit_text(prompts.get(ctype, "Отправь контент:"), reply_markup=kb_cancel_admin())

@dp.message(AdminFSM.send_content)
async def admin_save_content(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data  = await state.get_data()
    code  = data["new_code"]
    ctype = data["content_type"]
    db    = load_db()
    entry = {"type": ctype}
    if ctype in ("text", "link"):
        if not message.text:
            await message.answer("⚠️ Нужен текст. Попробуй снова:")
            return
        entry["content"] = message.text
    elif ctype == "photo":
        if not message.photo:
            await message.answer("⚠️ Нужно фото. Попробуй снова:")
            return
        entry["content"] = message.photo[-1].file_id
        entry["caption"] = message.caption or ""
    elif ctype == "video":
        if not message.video:
            await message.answer("⚠️ Нужно видео. Попробуй снова:")
            return
        entry["content"] = message.video.file_id
        entry["caption"] = message.caption or ""
    elif ctype == "file":
        if not message.document:
            await message.answer("⚠️ Нужен файл. Попробуй снова:")
            return
        entry["content"] = message.document.file_id
        entry["caption"] = message.caption or ""
    db["codes"][code] = entry
    save_db(db)
    await state.clear()
    await message.answer(
        f"✅ Код *{code}* сохранён!\nТип: `{ctype}`",
        parse_mode="Markdown",
        reply_markup=kb_admin()
    )

@dp.callback_query(F.data == "admin_codes")
async def cb_admin_codes(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    await state.clear()
    db    = load_db()
    codes = db["codes"]
    if not codes:
        await callback.message.edit_text("📦 Кодов пока нет.", reply_markup=kb_back_admin())
        return
    await callback.message.edit_text(
        f"📦 *Список кодов* — всего: {len(codes)}",
        parse_mode="Markdown",
        reply_markup=build_codes_kb(codes)
    )

@dp.callback_query(F.data.startswith("view_"))
async def cb_view_code(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    code = callback.data.replace("view_", "")
    db   = load_db()
    if code not in db["codes"]:
        await callback.answer("Код не найден.", show_alert=True)
        return
    entry   = db["codes"][code]
    preview = str(entry.get("content", ""))[:60]
    text = (
        f"🔑 *Код:* `{code}`\n"
        f"📋 *Тип:* {entry['type']}\n"
        f"📄 *Содержимое:* `{preview}`"
    )
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить",      callback_data=f"ask_del_{code}")],
        [InlineKeyboardButton(text="◀️ К списку кодов", callback_data="admin_codes")],
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)

@dp.callback_query(F.data.startswith("ask_del_"))
async def cb_ask_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    code = callback.data.replace("ask_del_", "")
    await callback.message.edit_text(
        f"🗑 Удалить код *{code}*?\n\nЭто действие необратимо.",
        parse_mode="Markdown",
        reply_markup=kb_confirm_del(code)
    )

@dp.callback_query(F.data.startswith("del_yes_"))
async def cb_confirm_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ Нет доступа.", show_alert=True)
        return
    code = callback.data.replace("del_yes_", "")
    db   = load_db()
    if code in db["codes"]:
        del db["codes"][code]
        save_db(db)
        await callback.answer(f"✅ Код {code} удалён.", show_alert=True)
    else:
        await callback.answer("❌ Код уже не существует.", show_alert=True)
    codes = db["codes"]
    if not codes:
        await callback.message.edit_text("📦 Кодов пока нет.", reply_markup=kb_back_admin())
    else:
        await callback.message.edit_text(
            f"📦 *Список кодов* — всего: {len(codes)}",
            parse_mode="Markdown",
            reply_markup=build_codes_kb(codes)
        )

# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────

async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
