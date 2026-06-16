import random
import string
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import UserRepository


class UserService:

    def __init__(self):
        self.repo = UserRepository()

    def generate_referral_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    async def get_or_create_user(self, session: AsyncSession, tg_user):

        user = await self.repo.get_by_telegram_id(session, tg_user.id)

        if user:
            user.last_activity_at = datetime.utcnow()
            await session.commit()
            return user

        new_user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            referral_code=self.generate_referral_code(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow()
        )

        return await self.repo.create(session, new_user)
