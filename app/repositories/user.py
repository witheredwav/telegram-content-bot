from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:

    async def get_by_telegram_id(self, session: AsyncSession, telegram_id: int):
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, user: User):
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
