from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import WORKS_LINK


def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться", url="https://t.me/your_channel")],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check")]
    ])


def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Примеры работ", url=WORKS_LINK)],
        [InlineKeyboardButton(text="Ввести код", callback_data="code")]
    ])
