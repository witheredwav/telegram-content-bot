from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


class OrderService:

    async def create_order(
        self,
        session: AsyncSession,
        user_id: int,
        request_type: str,
        amount: int
    ):

        order = Order(
            user_id=user_id,
            request_type=request_type,
            amount=amount,
            status="pending"
        )

        session.add(order)
        await session.commit()
        await session.refresh(order)

        return order

    async def mark_as_paid(
        self,
        session: AsyncSession,
        order_id: int
    ):

        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status="paid")
        )

        await session.commit()

    async def get_orders(self, session: AsyncSession):
        result = await session.execute(
            select(Order).order_by(Order.created_at.desc())
        )
        return result.scalars().all()
