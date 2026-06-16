from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.repositories.request_repository import RequestRepository
from app.repositories.stats_repository import StatsRepository


class AnalyticsService:

    def __init__(self):
        self.orders = OrderRepository()
        self.requests = RequestRepository()
        self.stats = StatsRepository()

    async def get_full_stats(self, session: AsyncSession):

        users = await self.stats.get_users_count(session)
        referrals = await self.stats.get_referrals_count(session)

        orders = await self.orders.get_paid_count(session)
        income = await self.orders.get_total_income(session)

        requests = await self.requests.get_all(session)

        conversion = 0
        if len(requests) > 0:
            conversion = round((orders / len(requests)) * 100, 2)

        return {
            "users": users,
            "referrals": referrals,
            "orders": orders,
            "income": income,
            "requests": len(requests),
            "conversion": conversion
        }
