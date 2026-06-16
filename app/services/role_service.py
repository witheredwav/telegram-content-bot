from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import UserRole


class RoleService:

    async def get_role(self, session: AsyncSession, user_id: int):

        result = await session.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )

        role = result.scalar_one_or_none()

        if not role:
            return "user"

        return role.role

    async def set_role(
        self,
        session: AsyncSession,
        user_id: int,
        role: str
    ):

        result = await session.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )

        obj = result.scalar_one_or_none()

        if obj:
            obj.role = role
        else:
            obj = UserRole(user_id=user_id, role=role)
            session.add(obj)

        await session.commit()
