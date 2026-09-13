"""
CRUD-эндпоинты для Monitor.

Все эндпоинты защищены — требуют JWT-токен.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Monitor, User
from app.schemas.monitor import MonitorCreate, MonitorRead, MonitorUpdate
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