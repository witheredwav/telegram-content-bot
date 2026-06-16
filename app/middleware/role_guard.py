from aiogram import BaseMiddleware
from app.database.session import async_session
from app.services.role_service import RoleService


class RoleGuardMiddleware(BaseMiddleware):

    def __init__(self, required_role: str = "admin"):
        self.required_role = required_role
        self.service = RoleService()

    async def __call__(self, handler, event, data):

        user = event.from_user

        async with async_session() as session:

            role = await self.service.get_role(session, user.id)

            if self.required_role == "admin" and role != "admin":
                return  # блокируем доступ

            if self.required_role == "manager":
                if role not in ["admin", "manager"]:
                    return

        return await handler(event, data)
