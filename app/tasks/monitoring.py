"""
Фоновые задачи мониторинга.

Celery worker выполняет эти функции.
"""

import asyncio

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Monitor, Check
from app.services.checker import check_url


# ============================================
# Проверка одного монитора
# ============================================
@celery_app.task(name="app.tasks.monitoring.check_monitor")
def check_monitor(monitor_id: int) -> dict:
    """
    Проверяет один монитор по ID.

    Синхронная задача (Celery не работает с async).
    Внутри запускает async-функцию check_url через asyncio.run().
    """
    db = SessionLocal()
    try:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        if not monitor:
            return {"error": f"Monitor {monitor_id} not found"}

        if not monitor.is_active:
            return {"monitor_id": monitor_id, "skipped": "inactive"}

        # Запускаем асинхронную проверку
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

        return {
            "monitor_id": monitor_id,
            "status_code": result.status_code,
            "response_time_ms": result.response_time_ms,
            "is_success": result.is_success,
        }

    except Exception as e:
        db.rollback()
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
            # Кидаем задачу в очередь (не выполняем сразу)
            check_monitor.delay(monitor.id)
            count += 1

        return {
            "queued": count,
            "message": f"Задач в очередь: {count}",
        }

    finally:
        db.close()