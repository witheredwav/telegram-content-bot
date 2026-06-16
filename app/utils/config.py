from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379"

    CHANNEL_ID: str | None = None
    CHANNEL_USERNAME: str | None = None

    WORKS_CHANNEL_ID: str | None = None
    WORKS_CHANNEL_USERNAME: str | None = None

    ADMIN_IDS: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
