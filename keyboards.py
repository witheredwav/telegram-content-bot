from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/YOUR_CHANNEL")],
        [InlineKeyboardButton(text="✅ Проверить", callback_data="check")]
    ])


def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Работы", url="https://t.me/YOUR_CHANNEL")],
        [InlineKeyboardButton(text="👥 Рефералка", callback_data="ref")],
        [InlineKeyboardButton(text="🔑 Код", callback_data="code")]
    ])


def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="📦 Коды", callback_data="admin_codes")
        ],
        [
            InlineKeyboardButton(text="🎲 Создать код", callback_data="admin_create"),
            InlineKeyboardButton(text="🗑 Удалить код", callback_data="admin_delete")
        ],
        [
            InlineKeyboardButton(text="👥 Рефералы", callback_data="admin_refs")
        ]
    ])
