from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.promo_code import PromoCode


class StatsRepository:

    async def get_users_count(self, session: AsyncSession):
        result = await session.execute(
            select(func.count(User.id))
        )
        return result.scalar()

    async def get_subscribed_count(self, session: AsyncSession):
        result = await session.execute(
            select(func.count(User.id)).where(User.is_subscribed == True)
        )
        return result.scalar()

    async def get_referrals_count(self, session: AsyncSession):
        result = await session.execute(
            select(func.sum(User.referrals_count))
        )
        return result.scalar() or 0

    async def get_codes_used(self, session: AsyncSession):
        result = await session.execute(
            select(func.sum(PromoCode.used_count))
        )
        return result.scalar() or 0
