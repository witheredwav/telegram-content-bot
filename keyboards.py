from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_LINK, PORTFOLIO_LINK


# ================= START =================
def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔗 Подписаться", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check")]
    ])


# ================= MAIN =================
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📂 Примеры работ", url=PORTFOLIO_LINK)],
        [InlineKeyboardButton("🔑 Ввести реф код", callback_data="enter_ref")],
        [InlineKeyboardButton("👥 Рефералы", callback_data="ref_menu")]
    ])


# ================= REF MENU =================
def ref_kb(has_code: bool):
    kb = []

    if not has_code:
        kb.append([InlineKeyboardButton("➕ Создать реф код", callback_data="create_ref")])

    kb.append([InlineKeyboardButton("📋 Мой код", callback_data="my_ref")])

    return InlineKeyboardMarkup(inline_keyboard=kb)


# ================= ADMIN =================
def admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("➕ Код", callback_data="admin_add_code")],
        [InlineKeyboardButton("📦 Коды", callback_data="admin_codes")],
        [InlineKeyboardButton("❌ Удалить код", callback_data="admin_delete_code")],
        [InlineKeyboardButton("👥 Рефералы", callback_data="admin_refs")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]
    ])
