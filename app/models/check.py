"""
Модель Check — результат одной проверки монитора.
"""

from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Check(Base):
    """
    Результат проверки монитора в момент времени.

    Поля:
      - id: уникальный идентификатор
      - monitor_id: ID монитора (FK)
      - status_code: HTTP-код ответа (200, 404, 500 и т.д.)
      - response_time_ms: время ответа в миллисекундах
      - is_success: успешна ли проверка (2xx/3xx)
      - error: текст ошибки, если была
      - checked_at: когда проверяли
    """

    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    monitor_id: Mapped[int] = mapped_column(
        ForeignKey("monitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # HTTP-код ответа (может быть NULL, если не удалось подключиться)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Время ответа в мс (может быть NULL при ошибке)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Успешна ли (2xx/3xx = True)
    is_success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Текст ошибки (если была)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # ============================================
    # Связь с Monitor
    # ============================================
    monitor: Mapped["Monitor"] = relationship("Monitor", back_populates="checks")

    def __repr__(self) -> str:
        return f"<Check(id={self.id}, monitor_id={self.monitor_id}, success={self.is_success})>"