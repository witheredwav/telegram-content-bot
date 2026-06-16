import asyncio
import logging
import sqlite3
import os
import random

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

CHANNEL_LINK = os.getenv("CHANNEL_LINK")
WORKS_CHANNEL_LINK = os.getenv("WORKS_CHANNEL_LINK")
DM_LINK = os.getenv("DM_LINK")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- DB ----------------
conn = sqlite3.connect("data.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    content TEXT,
    type TEXT
)
""")

conn.commit()

# ---------------- STATE ----------------
user_state = {}
admin_state = {}

# ---------------- STATS ----------------
def stat(k):
    cur.execute("INSERT OR IGNORE INTO stats(key,count) VALUES(?,0)", (k,))
    cur.execute("UPDATE stats SET count=count+1 WHERE key=?", (k,))
    conn.commit()

# ---------------- KEYBOARDS ----------------
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Подписаться", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Проверить", callback_data="check")],
        [InlineKeyboardButton(text="🎧 Примеры", url=WORKS_CHANNEL_LINK)],
        [InlineKeyboardButton(text="💬 Заказать", url=DM_LINK)],
        [InlineKeyboardButton(text="🔑 Код", callback_data="enter_code")]
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="➕ Создать код", callback_data="admin_create")],
        [InlineKeyboardButton(text="📦 Коды", callback_data="admin_codes")]
    ])

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Нет", callback_data="confirm_no")
        ]
    ])

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(m: Message):
    stat("start")
    await m.answer("👋 Меню:", reply_markup=main_kb())

# ---------------- CHECK ----------------
@dp.callback_query(F.data == "check")
async def check(c: CallbackQuery):
    stat("check")

    try:
        member = await bot.get_chat_member(CHANNEL_ID, c.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await c.message.answer("✅ Подписка есть")
        else:
            await c.message.answer("❌ Нет подписки")
    except:
        await c.message.answer("⚠️ Ошибка")

    await c.answer()

# ---------------- ENTER CODE ----------------
@dp.callback_query(F.data == "enter_code")
async def enter(c: CallbackQuery):
    user_state[c.from_user.id] = "code"
    await c.message.answer("🔑 Введи код:", reply_markup=cancel_kb())
    await c.answer()

# ---------------- CANCEL ----------------
@dp.callback_query(F.data == "cancel")
async def cancel(c: CallbackQuery):
    user_state.pop(c.from_user.id, None)
    await c.message.answer("❌ Отменено")
    await c.answer()

# ---------------- ADMIN PANEL ----------------
@dp.message(Command("admin"))
async def admin(m: Message):
    if m.from_user.id != ADMIN_ID:
        return
    await m.answer("⚙️ Админка:", reply_markup=admin_kb())

# ---------------- ADMIN STATS ----------------
@dp.callback_query(F.data == "admin_stats")
async def stats(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT * FROM stats")
    data = cur.fetchall()

    text = "📊 СТАТИСТИКА:\n\n"
    for k, v in data:
        text += f"{k}: {v}\n"

    await c.message.edit_text(text)
    await c.answer()

# ---------------- CREATE CODE STEP 1 ----------------
@dp.callback_query(F.data == "admin_create")
async def create(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(10000, 99999))
    admin_state["code"] = code

    await c.message.edit_text(
        f"➕ Код: {code}\n\nПодтвердить создание?",
        reply_markup=confirm_kb()
    )
    await c.answer()

# ---------------- CONFIRM YES ----------------
@dp.callback_query(F.data == "confirm_yes")
async def yes(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    await c.message.answer("📤 Отправь контент (текст/фото/видео)")
    await c.answer()

# ---------------- CONFIRM NO ----------------
@dp.callback_query(F.data == "confirm_no")
async def no(c: CallbackQuery):
    admin_state.pop("code", None)
    await c.message.answer("❌ Отменено")
    await c.answer()

# ---------------- ADMIN CODES ----------------
@dp.callback_query(F.data == "admin_codes")
async def codes(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT code FROM codes")
    rows = cur.fetchall()

    text = "📦 КОДЫ:\n\n" + "\n".join([r[0] for r in rows])

    await c.message.edit_text(text)
    await c.answer()

# ---------------- SAVE ADMIN CONTENT ----------------
@dp.message()
async def save(m: Message):
    uid = m.from_user.id

    # USER CODE MODE
    if user_state.get(uid) == "code":
        text = (m.text or "").strip()

        if text.startswith("/"):
            return

        cur.execute("SELECT content FROM codes WHERE code=?", (text,))
        row = cur.fetchone()

        if row:
            await m.answer(f"📦 Контент:\n\n{row[0]}")
        else:
            await m.answer("❌ Неверный код")

        return

    # ADMIN CONTENT MODE
    if uid == ADMIN_ID and "code" in admin_state:
        code = admin_state["code"]

        content = ""
        if m.text:
            content = m.text
        elif m.photo:
            content = m.photo[-1].file_id
        elif m.video:
            content = m.video.file_id

        cur.execute("INSERT OR REPLACE INTO codes VALUES (?, ?, ?)", (code, content, "text"))
        conn.commit()

        admin_state.pop("code")

        await m.answer(f"✅ Код {code} сохранён")

# ---------------- RUN ----------------
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
