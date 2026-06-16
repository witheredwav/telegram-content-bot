from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def request_status_keyboard(request_id: int):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 В работу",
                    callback_data=f"req_in_progress_{request_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Завершить",
                    callback_data=f"req_done_{request_id}"
                )
            ]
        ]
    )
