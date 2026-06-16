from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.session import async_session
from app.services.admin_service import AdminService
from app.services.admin_request_service import AdminRequestService
from app.keyboards.admin_requests import request_status_keyboard

router = Router()

admin_service = AdminService()
service = AdminRequestService()


# 📋 список заявок
@router.callback_query(F.data == "admin_requests")
async def admin_requests(callback: CallbackQuery):

    if not admin_service.is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    async with async_session() as session:

        requests = await service.get_requests(session)

    if not requests:
        await callback.message.answer("📭 Заявок пока нет")
        return

    text = "📋 <b>Заявки клиентов:</b>\n\n"

    for r in requests[:10]:
        text += (
            f"🆔 {r.id}\n"
            f"👤 user: {r.user_id}\n"
            f"📌 {r.request_type}\n"
            f"📄 {r.text[:30]}\n"
            f"📊 {r.status}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()


# 🔄 статус: в работу
@router.callback_query(F.data.startswith("req_in_progress_"))
async def set_in_progress(callback: CallbackQuery):

    request_id = int(callback.data.split("_")[-1])

    async with async_session() as session:

        await service.update_status(session, request_id, "in_progress")

    await callback.message.answer(f"🔄 Заявка {request_id} в работе")

    await callback.answer()


# ✅ статус: завершена
@router.callback_query(F.data.startswith("req_done_"))
async def set_done(callback: CallbackQuery):

    request_id = int(callback.data.split("_")[-1])

    async with async_session() as session:

        await service.update_status(session, request_id, "done")

    await callback.message.answer(f"✅ Заявка {request_id} завершена")

    await callback.answer()
