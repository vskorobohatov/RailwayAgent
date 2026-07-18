from datetime import date, datetime

from sqlalchemy import String, Integer, Float, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TrainArrival(Base):
    __tablename__ = "train_arrivals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, default_func=date.today)
    time: Mapped[str] = mapped_column(String(5))
    train_number: Mapped[str] = mapped_column(String(20))
    platform: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delay_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())