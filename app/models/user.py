"""
Модель пользователя.

Описывает таблицу 'users' в PostgreSQL.
Каждый атрибут класса = столбец таблицы.
"""

from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """
    Пользователь сервиса «Маяк».

    Поля:
      - id: уникальный идентификатор (автоинкремент)
      - email: почта (уникальная, используется для входа)
      - hashed_password: хэш пароля (никогда не храним пароль открыто!)
      - is_active: активен ли аккаунт
      - created_at: дата регистрации
    """

    __tablename__ = "users"     # имя таблицы в БД

    # ============================================
    # Столбцы таблицы
    # ============================================
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ============================================
    # Связь с Monitor (один-ко-многим)
    # ============================================
    monitors: Mapped[list["Monitor"]] = relationship(
        "Monitor",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"