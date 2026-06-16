from aiogram.types import (
InlineKeyboardMarkup,
InlineKeyboardButton
)

from config import WORKS_LINK

def start_keyboard():


return InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подписаться",
                url="https://t.me/witheredoff"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔍 Проверить подписку",
                callback_data="check_sub"
            )
        ]
    ]
)


def user_keyboard():


return InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📂 Пример работ",
                url=WORKS_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="🔑 Ввести код",
                callback_data="enter_code"
            )
        ]
    ]
)


def admin_keyboard():


return InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎲 Создать код",
                callback_data="create_code"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="stats"
            )
        ]
    ]
)


