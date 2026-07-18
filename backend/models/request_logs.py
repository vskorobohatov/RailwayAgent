from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    input_text: Mapped[str] = mapped_column(String(2000))
    ollama_response: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())