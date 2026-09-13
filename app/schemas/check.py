"""
Pydantic-схемы для Check.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CheckResult(BaseModel):
    """Результат проверки URL (не сохраняется в БД)."""
    status_code: int | None
    response_time_ms: int | None
    is_success: bool
    error: str | None


class CheckRead(BaseModel):
    """Схема ответа для Check."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    monitor_id: int
    status_code: int | None
    response_time_ms: int | None
    is_success: bool
    error: str | None
    checked_at: datetime


class MonitorStats(BaseModel):
    """Статистика по монитору."""
    monitor_id: int
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percent: float
    avg_response_time_ms: float | None
    last_check_at: datetime | None