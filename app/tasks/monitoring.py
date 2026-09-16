"""
Фоновые задачи мониторинга.

Celery worker выполняет эти функции.
Проверяет мониторы и шлёт алерты при падении.
"""

import asyncio
import logging

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Monitor, Check
from app.services.checker import check_url


logger = logging.getLogger(__name__)


# ============================================
# Проверка одного монитора
# ============================================
@celery_app.task(name="app.tasks.monitoring.check_monitor")
def check_monitor(monitor_id: int) -> dict:
    """
    Проверяет один монитор по ID.

    Если монитор упал — шлёт алерт в Telegram.
    """
    from app.tasks.alerts import send_down_alert, send_up_alert

    db = SessionLocal()
    try:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        if not monitor:
            return {"error": f"Monitor {monitor_id} not found"}

        if not monitor.is_active:
            return {"monitor_id": monitor_id, "skipped": "inactive"}

        # Была ли предыдущая проверка неуспешной?
        last_check = (
            db.query(Check)
            .filter(Check.monitor_id == monitor_id)
            .order_by(Check.checked_at.desc())
            .first()
        )
        was_down = last_check and not last_check.is_success

        # Проверяем URL
        result = asyncio.run(check_url(monitor.url))

        # Сохраняем результат
        check = Check(
            monitor_id=monitor.id,
            status_code=result.status_code,
            response_time_ms=result.response_time_ms,
            is_success=result.is_success,
            error=result.error,
        )
        db.add(check)
        db.commit()

        # ============================================
        # Алерты (только при смене статуса)
        # ============================================
        if not result.is_success:
            # Монитор упал
            if not was_down:
                # Только что упал — шлём алерт
                send_down_alert.delay(
                    monitor.id,
                    result.error or "Неизвестная ошибка",
                )
                logger.info(f"Monitor {monitor_id}: DOWN — алерт отправлен")
        else:
            # Монитор работает
            if was_down:
                # Только что восстановился
                send_up_alert.delay(monitor.id)
                logger.info(f"Monitor {monitor_id}: UP — сообщение отправлено")

        return {
            "monitor_id": monitor_id,
            "status_code": result.status_code,
            "response_time_ms": result.response_time_ms,
            "is_success": result.is_success,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Monitor {monitor_id} check failed: {e}")
        return {"monitor_id": monitor_id, "error": str(e)}
    finally:
        db.close()


# ============================================
# Проверка всех активных мониторов
# ============================================
@celery_app.task(name="app.tasks.monitoring.check_all_monitors")
def check_all_monitors() -> dict:
    """
    Проверяет все активные мониторы.

    Запускается по расписанию (Celery Beat).
    """
    db = SessionLocal()
    try:
        monitors = db.query(Monitor).filter(Monitor.is_active.is_(True)).all()

        count = 0
        for monitor in monitors:
            check_monitor.delay(monitor.id)
            count += 1

        return {
            "queued": count,
            "message": f"Задач в очередь: {count}",
        }

    finally:
        db.close()