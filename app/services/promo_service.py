from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.promo_repository import PromoRepository


class PromoService:

    def __init__(self):
        self.repo = PromoRepository()

    async def use_code(self, session: AsyncSession, code: str):

        promo = await self.repo.get_by_code(session, code)

        if not promo:
            return None, "❌ Код не найден"

        if not promo.is_active:
            return None, "❌ Код не активен"

        if promo.expires_at and promo.expires_at < datetime.utcnow():
            return None, "❌ Код истёк"

        if promo.used_count >= promo.max_uses:
            return None, "❌ Лимит активаций исчерпан"

        promo.used_count += 1

        await session.commit()

        return promo, "✅ Код активирован"
