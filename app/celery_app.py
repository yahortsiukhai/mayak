"""
Конфигурация Celery.

Celery — фоновые задачи.
Redis — брокер (посредник).
"""

from celery import Celery
from celery.schedules import crontab

from app.config import settings


# ============================================
# Создаём Celery-приложение
# ============================================
celery_app = Celery(
    "mayak",
    broker=settings.redis_url,        # откуда брать задачи
    backend=settings.redis_url,       # куда складывать результаты
    include=[
        "app.tasks.monitoring",  
        "app.tasks.alerts",     # список модулей с задачами
    ],
)


# ============================================
# Настройки Celery
# ============================================
celery_app.conf.update(
    # Формат данных
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Часовой пояс
    timezone="UTC",
    enable_utc=True,

    # Хранить результаты 1 час
    result_expires=3600,

    # Ограничения (защита от зависаний)
    task_time_limit=300,              # максимум 5 минут на задачу
    task_soft_time_limit=240,         # мягкий лимит 4 минуты

    # Перезапускать worker, если задача упала
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


# ============================================
# Расписание (Celery Beat)
# ============================================
celery_app.conf.beat_schedule = {
    # Каждый час проверять все активные мониторы
    "check-all-monitors-hourly": {
        "task": "app.tasks.monitoring.check_all_monitors",
        "schedule": crontab(minute=0),  # в 00 минут каждого часа
    },
}