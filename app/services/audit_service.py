from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:

    def __init__(self):
        self.repo = AuditRepository()

    async def log(
        self,
        session: AsyncSession,
        user_id: int,
        action: str,
        target: str = None,
        meta: str = None
    ):

        log = AuditLog(
            user_id=user_id,
            action=action,
            target=target,
            meta=meta
        )

        await self.repo.create(session, log)
