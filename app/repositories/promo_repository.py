from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promo_code import PromoCode


class PromoRepository:

    async def get_by_code(self, session: AsyncSession, code: str):
        result = await session.execute(
            select(PromoCode).where(PromoCode.code == code)
        )
        return result.scalar_one_or_none()

    async def save(self, session: AsyncSession, promo: PromoCode):
        session.add(promo)
        await session.commit()
        await session.refresh(promo)
        return promo
