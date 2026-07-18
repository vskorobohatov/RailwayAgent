from datetime import date, datetime

from sqlalchemy import String, Integer, Float, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class WaitingRoom(Base):
    __tablename__ = "waiting_room"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, default_func=date.today)
    visitors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tea_cups: Mapped[int | None] = mapped_column(Integer, nullable=True)
    water_glasses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
