from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.antifraud import AntiFraudLog


class AntiFraudService:

    async def is_spam(self, session: AsyncSession, user_id: int) -> bool:

        # считаем действия за последнюю минуту
        one_minute_ago = datetime.utcnow() - timedelta(seconds=60)

        result = await session.execute(
            select(func.count(AntiFraudLog.id))
            .where(AntiFraudLog.user_id == user_id)
            .where(AntiFraudLog.created_at >= one_minute_ago)
        )

        count = result.scalar()

        return count > 10  # лимит: 10 действий в минуту

    async def log_action(
        self,
        session: AsyncSession,
        user_id: int,
        action: str,
        status: str = "allowed"
    ):

        log = AntiFraudLog(
            user_id=user_id,
            action=action,
            status=status
        )

        session.add(log)
        await session.commit()
