from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
WORKS_LINK = os.getenv("WORKS_LINK")
