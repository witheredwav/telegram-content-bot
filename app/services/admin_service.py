from app.utils.config import settings


class AdminService:

    def is_admin(self, user_id: int) -> bool:

        admin_ids = settings.ADMIN_IDS.split(",")

        return str(user_id) in admin_ids
