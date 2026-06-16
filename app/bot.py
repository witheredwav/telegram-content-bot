from aiogram import Bot, Dispatcher
from app.utils.config import settings

# 🔥 бот
bot = Bot(token=settings.BOT_TOKEN)

# 🔥 диспетчер (ЭТО ТЫ ЗАБЫЛ)
dp = Dispatcher()
