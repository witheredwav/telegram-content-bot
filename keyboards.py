from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

CHANNEL_LINK = "https://t.me/witheredoff"
WORKS_LINK = "https://t.me/witheredwav"


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="🔍 Проверить подписку", callback_data="check")]
    ])


def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Примеры работ", url=WORKS_LINK)],
        [InlineKeyboardButton(text="🔑 Ввести код", callback_data="code")]
    ])
