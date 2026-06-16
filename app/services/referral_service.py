from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class ReferralService:

    async def process_referral(
        self,
        session: AsyncSession,
        new_user: User,
        referral_code: str | None
    ):

        # если нет кода — ничего не делаем
        if not referral_code:
            return

        # защита от самореферала
        if new_user.referral_code == referral_code:
            return

        # ищем пригласившего
        result = await session.execute(
            select(User).where(User.referral_code == referral_code)
        )

        inviter = result.scalar_one_or_none()

        if not inviter:
            return

        # защита: нельзя пригласить самого себя
        if inviter.telegram_id == new_user.telegram_id:
            return

        # привязываем реферала
        new_user.invited_by = inviter.telegram_id

        # увеличиваем счётчик
        inviter.referrals_count += 1

        # начисляем скидку
        if inviter.referrals_count >= 20:
            inviter.discount_percent = 20
        elif inviter.referrals_count >= 10:
            inviter.discount_percent = 15
        elif inviter.referrals_count >= 5:
            inviter.discount_percent = 10

        session.add(inviter)
        session.add(new_user)

        await session.commit()
