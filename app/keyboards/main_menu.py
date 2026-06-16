from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎧 Примеры работ",
                    callback_data="works"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎁 Ввести код",
                    callback_data="enter_code"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Рефералы",
                    callback_data="referrals"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📩 Оставить заявку",
                    callback_data="request"
                )
            ]
        ]
    )
