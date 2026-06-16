import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "your_channel")

CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/your_channel")

WORKS_LINK = os.getenv("WORKS_LINK", "https://t.me/your_examples")
