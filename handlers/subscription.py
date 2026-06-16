from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ChatMemberStatus

from config import CHANNEL_USERNAME
from keyboards import user_keyboard

router = Router()

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):

```
user_id = callback.from_user.id

try:
    member = await callback.bot.get_chat_member(
        chat_id=f"@{CHANNEL_USERNAME}",
        user_id=user_id
    )

    if member.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    ]:

        await callback.message.answer(
            "✅ Подписка подтверждена!\n\n"
            "Теперь тебе доступны функции:",
            reply_markup=user_keyboard()
        )

    else:
        await callback.message.answer(
            "❌ Ты не подписан на канал!\n"
            "Подпишись и нажми кнопку снова."
        )

except Exception as e:
    await callback.message.answer(
        "❌ Ошибка проверки подписки.\n"
        "Проверь username канала в .env"
    )

await callback.answer()
```
