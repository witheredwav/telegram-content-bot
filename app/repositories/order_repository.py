from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


class OrderRepository:

    async def get_all(self, session: AsyncSession):
        result = await session.execute(
            select(Order)
        )
        return result.scalars().all()

    async def get_paid_count(self, session: AsyncSession):
        result = await session.execute(
            select(func.count(Order.id)).where(Order.status == "paid")
        )
        return result.scalar()

    async def get_total_income(self, session: AsyncSession):
        result = await session.execute(
            select(func.sum(Order.amount)).where(Order.status == "paid")
        )
        return result.scalar() or 0
