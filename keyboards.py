from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/YOUR_CHANNEL")],
        [InlineKeyboardButton(text="✅ Проверить", callback_data="check")]
    ])


def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Примеры работ", url="https://t.me/YOUR_CHANNEL")],
        [InlineKeyboardButton(text="🔑 Ввести код", callback_data="code")]
    ])


def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton(text="📦 Коды", callback_data="codes")],
        [InlineKeyboardButton(text="🗑 Удалить код", callback_data="del_menu")],
        [InlineKeyboardButton(text="🎲 Создать код", callback_data="create")]
    ])
