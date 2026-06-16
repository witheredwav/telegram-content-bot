from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):

    BOT_TOKEN: str

    DATABASE_URL: str

    REDIS_URL: str

    ADMIN_IDS: str

    CHANNEL_ID: int
    CHANNEL_USERNAME: str

    WORKS_CHANNEL_ID: int
    WORKS_CHANNEL_USERNAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
