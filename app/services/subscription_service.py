from aiogram import Bot

from app.utils.config import settings


class SubscriptionService:

    async def is_subscribed(self, bot: Bot, user_id: int) -> bool:

        try:
            member = await bot.get_chat_member(
                chat_id=settings.CHANNEL_ID,
                user_id=user_id
            )

            status = member.status

            return status in ["member", "administrator", "creator"]

        except Exception:
            return False
