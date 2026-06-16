from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.database.session import async_session
from app.services.antifraud_service import AntiFraudService


class AntiFraudMiddleware(BaseMiddleware):

    def __init__(self):
        self.service = AntiFraudService()

    async def __call__(self, handler, event, data):

        user = event.from_user

        async with async_session() as session:

            spam = await self.service.is_spam(session, user.id)

            if spam:

                await self.service.log_action(
                    session,
                    user.id,
                    "spam_detected",
                    "blocked"
                )

                if isinstance(event, Message):
                    await event.answer("⛔ Слишком много действий. Подожди немного.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("⛔ Slow down", show_alert=True)

                return

            await self.service.log_action(
                session,
                user.id,
                "action",
                "allowed"
            )

        return await handler(event, data)
