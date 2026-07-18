from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Evacuation(Base):
    __tablename__ = "evacuations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, default_func=date.today)
    start_time: Mapped[str] = mapped_column(String(5))
    end_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())