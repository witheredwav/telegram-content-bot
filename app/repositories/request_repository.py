from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request


class RequestRepository:

    async def create(self, session: AsyncSession, request: Request):
        session.add(request)
        await session.commit()
        await session.refresh(request)
        return request

    async def get_all(self, session: AsyncSession):
        result = await session.execute(
            select(Request).order_by(Request.created_at.desc())
        )
        return result.scalars().all()
