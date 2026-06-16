from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str

    DATABASE_URL: str

    REDIS_URL: str

    CHANNEL_ID: int
    CHANNEL_USERNAME: str

    WORKS_CHANNEL_ID: int
    WORKS_CHANNEL_USERNAME: str

    ADMIN_IDS: str  # можно парсить позже

    class Config:
        env_file = ".env"


settings = Settings()
