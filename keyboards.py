from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_LINK, PORTFOLIO_LINK


# ================= START =================
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔗 Подписаться",
                url=CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Проверить подписку",
                callback_data="check"
            )
        ]
    ])


# ================= MAIN MENU =================
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📂 Примеры работ",
                url=PORTFOLIO_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="🔑 Ввести код",
                callback_data="code"
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 Рефералы",
                callback_data="ref"
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Моя статистика",
                callback_data="mystats"
            )
        ]
    ])
