from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_LINK, PORTFOLIO_LINK


def start_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
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
        ]
    )


def main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Примеры работ",
                    url=PORTFOLIO_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔑 Ввести реф код",
                    callback_data="enter_ref"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Реферальная система",
                    callback_data="ref_menu"
                )
            ]
        ]
    )


def ref_kb(has_code=False):
    rows = []

    if not has_code:
        rows.append([
            InlineKeyboardButton(
                text="➕ Создать реферальный код",
                callback_data="create_ref"
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="📋 Мой код",
            callback_data="my_ref"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def admin_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Создать код",
                    callback_data="admin_create_code"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📦 Все коды",
                    callback_data="admin_codes"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Рефералы",
                    callback_data="admin_refs"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats"
                )
            ]
        ]
    )
