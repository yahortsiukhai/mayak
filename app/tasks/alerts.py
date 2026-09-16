"""
Celery-задачи для отправки алертов в Telegram.
"""

import asyncio
import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Monitor
from app.services.telegram import (
    send_message,
    format_down_alert,
    format_up_alert,
)


logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.alerts.send_down_alert")
def send_down_alert(monitor_id: int, error: str) -> dict:
    """
    Отправляет алерт о падении монитора.
    """
    db = SessionLocal()
    try:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        if not monitor:
            return {"error": "monitor not found"}

        user = monitor.user
        if not user or not user.telegram_chat_id:
            logger.warning(
                f"Monitor {monitor_id}: у пользователя нет telegram_chat_id"
            )
            return {"error": "no telegram_chat_id"}

        text = format_down_alert(monitor.name, monitor.url, error)

        success = asyncio.run(send_message(user.telegram_chat_id, text))

        return {
            "monitor_id": monitor_id,
            "sent": success,
            "chat_id": user.telegram_chat_id,
        }

    finally:
        db.close()


@celery_app.task(name="app.tasks.alerts.send_up_alert")
def send_up_alert(monitor_id: int) -> dict:
    """Отправляет сообщение о восстановлении."""
    db = SessionLocal()
    try:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        if not monitor:
            return {"error": "monitor not found"}

        user = monitor.user
        if not user or not user.telegram_chat_id:
            return {"error": "no telegram_chat_id"}

        text = format_up_alert(monitor.name)

        success = asyncio.run(send_message(user.telegram_chat_id, text))

        return {"monitor_id": monitor_id, "sent": success}

    finally:
        db.close()