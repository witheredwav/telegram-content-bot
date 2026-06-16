from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database.base import Base


class AntiFraudLog(Base):
    __tablename__ = "antifraud_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, index=True)

    action: Mapped[str] = mapped_column(String(100))

    status: Mapped[str] = mapped_column(String(50))  # allowed / blocked / warning

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
