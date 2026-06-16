import asyncio
import logging
import sqlite3
import os
import random
from datetime import datetime, date

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
WORKS_CHANNEL_LINK = os.getenv("WORKS_CHANNEL_LINK")
DM_LINK = os.getenv("DM_LINK")

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


def stat(key):
    cur.execute("INSERT OR IGNORE INTO stats(key, count) VALUES(?, 0)", (key,))
    cur.execute("UPDATE stats SET count = count + 1 WHERE key = ?", (key,))
    conn.commit()


# ---------------- KEYBOARD ----------------
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Подписаться", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")],
        [InlineKeyboardButton(text="🎧 Примеры работ", url=WORKS_CHANNEL_LINK)],
        [InlineKeyboardButton(text="💬 Заказать сведение", url=DM_LINK)],
        [InlineKeyboardButton(text="🔑 Ввести ключ", callback_data="enter_code")]
    ])


def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="➕ Создать код", callback_data="create_code")],
        [InlineKeyboardButton(text="📦 Коды", callback_data="list_codes")],
    ])


# ---------------- START ----------------
@dp.message(Command("start"))
async def start(m: Message):
    stat("start")
    await m.answer("👋 Привет! Выбери действие:", reply_markup=main_kb())


# ---------------- CHECK SUB ----------------
@dp.callback_query(F.data == "check_sub")
async def check_sub(c: CallbackQuery):
    stat("check_sub")
    try:
        member = await bot.get_chat_member(CHANNEL_ID, c.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await c.message.answer("✅ Ты подписан")
        else:
            await c.message.answer("❌ Ты не подписан")
    except:
        await c.message.answer("⚠️ Ошибка проверки")
    await c.answer()


# ---------------- ENTER CODE ----------------
@dp.callback_query(F.data == "enter_code")
async def enter_code(c: CallbackQuery):
    stat("enter_code")
    await c.message.answer("🔑 Введи 5-значный код:")
    await c.answer()


# ---------------- TEXT HANDLER ----------------
@dp.message()
async def text(m: Message):
    txt = m.text.strip()

    # проверка кода
    cur.execute("SELECT content, type FROM codes WHERE code=?", (txt,))
    row = cur.fetchone()

    if row:
        content, ctype = row
        await m.answer(f"📦 Контент:\n\n{content}")
    else:
        await m.answer("❌ Неверный код")


# ---------------- ADMIN PANEL ----------------
admin_state = {}

@dp.message(Command("admin"))
async def admin(m: Message):
    if m.from_user.id != ADMIN_ID:
        return
    await m.answer("⚙️ Админ-панель", reply_markup=admin_kb())


# -------- STATS --------
@dp.callback_query(F.data == "admin_stats")
async def stats(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT * FROM stats")
    rows = cur.fetchall()

    text = "📊 СТАТИСТИКА:\n\n"
    for k, v in rows:
        text += f"{k}: {v}\n"

    await c.message.answer(text)
    await c.answer()


# -------- CREATE CODE FLOW --------
@dp.callback_query(F.data == "create_code")
async def create_code(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(10000, 99999))
    admin_state[c.from_user.id] = {"code": code}

    await c.message.answer(f"➕ Код создан: {code}\nТеперь отправь контент (текст/фото/видео/ссылку)")
    await c.answer()


# receive admin content
@dp.message()
async def admin_content(m: Message):
    if m.from_user.id != ADMIN_ID:
        return

    if m.from_user.id in admin_state:
        code = admin_state[m.from_user.id]["code"]

        content = ""
        ctype = ""

        if m.text:
            content = m.text
            ctype = "text"
        elif m.photo:
            content = m.photo[-1].file_id
            ctype = "photo"
        elif m.video:
            content = m.video.file_id
            ctype = "video"
        else:
            content = "unsupported"
            ctype = "text"

        cur.execute("INSERT OR REPLACE INTO codes VALUES (?, ?, ?)", (code, content, ctype))
        conn.commit()

        del admin_state[m.from_user.id]

        await m.answer(f"✅ Код {code} сохранён")


# -------- LIST CODES --------
@dp.callback_query(F.data == "list_codes")
async def list_codes(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT code FROM codes")
    codes = cur.fetchall()

    text = "📦 КОДЫ:\n\n" + "\n".join([i[0] for i in codes])

    await c.message.answer(text)
    await c.answer()


# ---------------- MAIN ----------------
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
