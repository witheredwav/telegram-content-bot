from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request import Request
from app.repositories.request_repository import RequestRepository


class RequestService:

    def __init__(self):
        self.repo = RequestRepository()

    async def create_request(
        self,
        session: AsyncSession,
        user_id: int,
        request_type: str,
        text: str
    ):

        request = Request(
            user_id=user_id,
            request_type=request_type,
            text=text
        )

        return await self.repo.create(session, request)
