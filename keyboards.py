from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL = "https://t.me/your_channel"


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL)],
        [InlineKeyboardButton(text="🔍 Проверить подписку", callback_data="check")]
    ])
