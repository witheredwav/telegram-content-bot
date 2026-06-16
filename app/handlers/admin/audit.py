from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.admin_service import AdminService
from app.repositories.audit_repository import AuditRepository

router = Router()

admin_service = AdminService()
repo = AuditRepository()


@router.callback_query(F.data == "admin_audit")
async def audit_logs(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with async_session() as session:

        logs = await repo.get_all(session)

    if not logs:
        await callback.message.answer("📭 Логов нет")
        return

    text = "🧾 <b>Последние действия</b>\n\n"

    for log in logs[:15]:
        text += (
            f"👤 {log.user_id}\n"
            f"⚡ {log.action}\n"
            f"🎯 {log.target or '-'}\n"
            f"🕒 {log.created_at}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()
