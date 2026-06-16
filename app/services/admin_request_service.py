from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request


class AdminRequestService:

    async def get_requests(self, session: AsyncSession):
        result = await session.execute(
            select(Request).order_by(Request.created_at.desc())
        )
        return result.scalars().all()

    async def update_status(
        self,
        session: AsyncSession,
        request_id: int,
        status: str
    ):
        await session.execute(
            update(Request)
            .where(Request.id == request_id)
            .values(status=status)
        )
        await session.commit()
