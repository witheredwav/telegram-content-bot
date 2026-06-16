from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str

    REDIS_URL: Optional[str] = None

    CHANNEL_ID: int
    CHANNEL_USERNAME: str
    WORKS_CHANNEL_ID: int
    WORKS_CHANNEL_USERNAME: str
    ADMIN_IDS: str


settings = Settings()
