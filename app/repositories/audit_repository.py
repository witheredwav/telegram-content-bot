from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:

    async def create(self, session: AsyncSession, log: AuditLog):
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log

    async def get_all(self, session: AsyncSession):
        result = await session.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc())
        )
        return result.scalars().all()
