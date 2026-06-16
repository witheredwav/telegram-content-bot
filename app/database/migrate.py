from alembic.config import Config
from alembic import command
import os

from app.utils.logger import logger


def run_migrations():
    """
    Автоматически применяет все миграции при запуске бота
    """

    try:
        logger.info("Running database migrations...")

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        alembic_cfg_path = os.path.join(base_dir, "alembic.ini")

        alembic_cfg = Config(alembic_cfg_path)

        command.upgrade(alembic_cfg, "head")

        logger.info("Migrations applied successfully")

    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise
