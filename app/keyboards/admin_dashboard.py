from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_dashboard_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
                InlineKeyboardButton(text="📋 CRM", callback_data="admin_requests")
            ],
            [
                InlineKeyboardButton(text="💰 Заказы", callback_data="admin_orders"),
                InlineKeyboardButton(text="📈 Аналитика", callback_data="admin_analytics")
            ],
            [
                InlineKeyboardButton(text="🎁 Коды", callback_data="admin_create_code"),
                InlineKeyboardButton(text="👤 Пользователи", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton(text="📢 Рассылки", callback_data="admin_broadcast")
            ]
        ]
    )


def back_to_admin_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_dashboard")
            ]
        ]
    )
