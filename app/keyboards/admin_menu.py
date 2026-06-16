from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Создать код",
                    callback_data="admin_create_code"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Пользователи",
                    callback_data="admin_users"
                )
            ]
        ]
    )
