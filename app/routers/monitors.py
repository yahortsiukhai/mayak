"""
CRUD-эндпоинты для Monitor.

Все эндпоинты защищены — требуют JWT-токен.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Integer, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Monitor, User, Check
from app.schemas.monitor import MonitorCreate, MonitorRead, MonitorUpdate
from app.schemas.check import CheckRead, MonitorStats
from app.services.checker import check_url
from app.services.deps import get_current_user

router = APIRouter(prefix="/monitors", tags=["monitors"])


@router.post("/", response_model=MonitorRead, status_code=status.HTTP_201_CREATED)
def create_monitor(
    data: MonitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новый монитор."""
    monitor = Monitor(
        user_id=current_user.id,
        name=data.name,
        url=str(data.url),
        check_interval=data.check_interval,
        is_active=True,
    )
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.get("/", response_model=list[MonitorRead])
def list_monitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Список всех мониторов текущего пользователя."""
    monitors = (
        db.query(Monitor)
        .filter(Monitor.user_id == current_user.id)
        .order_by(Monitor.created_at.desc())
        .all()
    )
    return monitors


@router.get("/{monitor_id}", response_model=MonitorRead)
def get_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить один монитор по ID."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Монитор не найден",
        )
    return monitor


@router.patch("/{monitor_id}", response_model=MonitorRead)
def update_monitor(
    monitor_id: int,
    data: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить монитор (частично)."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Монитор не найден",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "url" and value is not None:
            value = str(value)
        setattr(monitor, field, value)

    db.commit()
    db.refresh(monitor)
    return monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить монитор."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Монитор не найден",
        )
    db.delete(monitor)
    db.commit()
    return None


# ============================================
# Проверки
# ============================================

@router.post("/{monitor_id}/check-now", response_model=CheckRead)
async def check_now(
    monitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Запустить проверку монитора прямо сейчас."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Монитор не найден",
        )

    result = await check_url(monitor.url)

    check = Check(
        monitor_id=monitor.id,
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        is_success=result.is_success,
        error=result.error,
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    return check


@router.get("/{monitor_id}/checks", response_model=list[CheckRead])
def list_checks(
    monitor_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """История проверок монитора."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Монитор не найден",
        )

    checks = (
        db.query(Check)
        .filter(Check.monitor_id == monitor.id)
        .order_by(Check.checked_at.desc())
        .limit(limit)
        .all()
    )
    return checks


@router.get("/{monitor_id}/stats", response_model=MonitorStats)
def get_monitor_stats(
    monitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Статистика по монитору."""
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == current_user.id)
        .first()
    )
    if not monitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Монитор не найден",
        )

    stats = (
        db.query(
            func.count(Check.id).label("total"),
            func.sum(func.cast(Check.is_success, Integer)).label("successful"),
            func.avg(Check.response_time_ms).label("avg_time"),
            func.max(Check.checked_at).label("last_check"),
        )
        .filter(Check.monitor_id == monitor.id)
        .first()
    )

    total = stats.total or 0
    successful = stats.successful or 0
    failed = total - successful
    uptime = (successful / total * 100) if total > 0 else 0.0

    return MonitorStats(
        monitor_id=monitor.id,
        total_checks=total,
        successful_checks=successful,
        failed_checks=failed,
        uptime_percent=round(uptime, 2),
        avg_response_time_ms=round(float(stats.avg_time), 2) if stats.avg_time else None,
        last_check_at=stats.last_check,
    )