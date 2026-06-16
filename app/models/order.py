from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, index=True)

    request_type: Mapped[str] = mapped_column(String(50))

    amount: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(30), default="pending")  # pending / paid

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
