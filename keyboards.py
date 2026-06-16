from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def user_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔑 Ввести код")],
            [KeyboardButton(text="🎬 Примеры")]
        ],
        resize_keyboard=True
    )


def admin_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎲 Новый код")],
            [KeyboardButton(text="📋 Коды")],
            [KeyboardButton(text="📊 Статистика")]
        ],
        resize_keyboard=True
    )
