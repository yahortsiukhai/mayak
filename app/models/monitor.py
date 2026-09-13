"""
Модель Monitor — что мониторит пользователь.

Каждый Monitor привязан к одному User (владельцу).
"""

from datetime import datetime

from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Monitor(Base):
    """
    Объект мониторинга.

    Поля:
      - id: уникальный идентификатор
      - user_id: ID владельца (FK на users.id)
      - name: название (для отображения)
      - url: URL для проверки
      - check_interval: интервал проверки в секундах
      - is_active: включён ли мониторинг
      - created_at: дата создания
    """

    __tablename__ = "monitors"

    # ============================================
    # Столбцы
    # ============================================
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    url: Mapped[str] = mapped_column(String(2048), nullable=False)

    check_interval: Mapped[int] = mapped_column(Integer, default=300, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ============================================
    # Связи
    # ============================================
    user: Mapped["User"] = relationship("User", back_populates="monitors")

    checks: Mapped[list["Check"]] = relationship(
        "Check",
        back_populates="monitor",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Monitor(id={self.id}, name={self.name}, url={self.url})>"