"""
Pydantic-схемы для пользователя.

Разделяют данные:
  - UserBase:    общие поля
  - UserCreate:  для регистрации (email + password)
  - UserRead:    для ответа API (без пароля!)
  - UserLogin:   для логина
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Общие поля пользователя."""
    email: EmailStr = Field(..., description="Email пользователя")


class UserCreate(UserBase):
    """Схема регистрации — приходит от клиента."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль (минимум 8 символов)",
    )


class UserLogin(UserBase):
    """Схема логина."""
    password: str = Field(..., description="Пароль")


class UserRead(UserBase):
    """Схема ответа — что отдаём клиенту (без пароля!)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime