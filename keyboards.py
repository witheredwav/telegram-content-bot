from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ================= START MENU =================
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Примеры работ", callback_data="portfolio")],
        [InlineKeyboardButton(text="🔑 Ввести код", callback_data="code")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="ref")],
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check")]
    ])


# ================= ADMIN MENU =================
def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="📦 Коды", callback_data="admin_codes")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="admin_refs")],
        [InlineKeyboardButton(text="➕ Выдать рефералы", callback_data="admin_add_refs")]
    ])
