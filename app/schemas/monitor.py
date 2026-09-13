"""
Pydantic-схемы для Monitor.
"""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class MonitorBase(BaseModel):
    """Общие поля."""
    name: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl = Field(..., description="URL для проверки")
    check_interval: int = Field(
        300,
        ge=60,
        le=86400,
        description="Интервал в секундах (60-86400)",
    )


class MonitorCreate(MonitorBase):
    """Схема создания — приходит от клиента."""
    pass


class MonitorUpdate(BaseModel):
    """Схема обновления — все поля опциональны."""
    name: str | None = Field(None, min_length=1, max_length=255)
    url: HttpUrl | None = None
    check_interval: int | None = Field(None, ge=60, le=86400)
    is_active: bool | None = None


class MonitorRead(MonitorBase):
    """Схема ответа."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    is_active: bool
    created_at: datetime