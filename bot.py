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
admin_temp = {}

# ---------------- STATS ----------------
def stat(key):
    cur.execute("INSERT OR IGNORE INTO stats(key, count) VALUES(?, 0)", (key,))
    cur.execute("UPDATE stats SET count = count + 1 WHERE key = ?", (key,))
    conn.commit()

# ---------------- KEYBOARDS ----------------
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Подписаться", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check")],
        [InlineKeyboardButton(text="🎧 Примеры работ", url=WORKS_CHANNEL_LINK)],
        [InlineKeyboardButton(text="💬 Заказать сведение", url=DM_LINK)],
        [InlineKeyboardButton(text="🔑 Ввести ключ", callback_data="enter_code")]
    ])

def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])

def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="➕ Создать код", callback_data="admin_create")],
        [InlineKeyboardButton(text="📦 Коды", callback_data="admin_codes")]
    ])

# ---------------- START ----------------
@dp.message(Command("start"))
async def start(m: Message):
    stat("start")
    await m.answer("👋 Главное меню:", reply_markup=main_kb())

# ---------------- ADMIN (ВАЖНО ИСПРАВЛЕНО) ----------------
@dp.message(Command("admin"))
async def admin(m: Message):
    if m.from_user.id != ADMIN_ID:
        return

    await m.answer("⚙️ Админ панель:", reply_markup=admin_kb())

# ---------------- CHECK SUB ----------------
@dp.callback_query(F.data == "check")
async def check(c: CallbackQuery):
    stat("check")

    try:
        member = await bot.get_chat_member(CHANNEL_ID, c.from_user.id)

        if member.status in ["member", "administrator", "creator"]:
            await c.message.answer("✅ Подписка подтверждена")
        else:
            await c.message.answer("❌ Ты не подписан")
    except:
        await c.message.answer("⚠️ Ошибка проверки")

    await c.answer()

# ---------------- ENTER CODE ----------------
@dp.callback_query(F.data == "enter_code")
async def enter_code(c: CallbackQuery):
    user_state[c.from_user.id] = "waiting_code"
    await c.message.answer("🔑 Введи код:", reply_markup=cancel_kb())
    await c.answer()

# ---------------- CANCEL ----------------
@dp.callback_query(F.data == "cancel")
async def cancel(c: CallbackQuery):
    user_state.pop(c.from_user.id, None)
    await c.message.answer("❌ Отменено")
    await c.answer()

# ---------------- CODE CHECK ----------------
@dp.message()
async def handle(m: Message):
    uid = m.from_user.id
    text = (m.text or "").strip()

    if user_state.get(uid) != "waiting_code":
        return

    if text.startswith("/"):
        return

    cur.execute("SELECT content FROM codes WHERE code=?", (text,))
    row = cur.fetchone()

    if row:
        await m.answer(f"📦 Контент:\n\n{row[0]}")
    else:
        await m.answer("❌ Неверный код")

# ---------------- ADMIN CALLBACKS ----------------
@dp.callback_query(F.data == "admin_stats")
async def stats(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT * FROM stats")
    data = cur.fetchall()

    msg = "📊 СТАТИСТИКА:\n\n"
    for k, v in data:
        msg += f"{k}: {v}\n"

    await c.message.answer(msg)
    await c.answer()

@dp.callback_query(F.data == "admin_create")
async def create(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    code = str(random.randint(10000, 99999))
    admin_temp[ADMIN_ID] = code

    await c.message.answer(f"➕ Код: {code}\nОтправь контент")
    await c.answer()

@dp.callback_query(F.data == "admin_codes")
async def codes(c: CallbackQuery):
    if c.from_user.id != ADMIN_ID:
        return

    cur.execute("SELECT code FROM codes")
    rows = cur.fetchall()

    text = "📦 КОДЫ:\n\n" + "\n".join([r[0] for r in rows])

    await c.message.answer(text)
    await c.answer()

# ---------------- SAVE ADMIN CONTENT ----------------
@dp.message()
async def save_admin(m: Message):
    if m.from_user.id != ADMIN_ID:
        return

    if ADMIN_ID not in admin_temp:
        return

    code = admin_temp[ADMIN_ID]

    content = ""
    ctype = "text"

    if m.text:
        content = m.text
    elif m.photo:
        content = m.photo[-1].file_id
        ctype = "photo"
    elif m.video:
        content = m.video.file_id
        ctype = "video"

    cur.execute("INSERT OR REPLACE INTO codes VALUES (?, ?, ?)", (code, content, ctype))
    conn.commit()

    del admin_temp[ADMIN_ID]

    await m.answer(f"✅ Код {code} сохранён")

# ---------------- RUN ----------------
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
