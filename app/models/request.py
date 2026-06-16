from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database.base import Base


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, index=True)

    request_type: Mapped[str] = mapped_column(String(50))

    text: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(String(30), default="new")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
