"""
UI-роутер: HTML-страницы.
"""

from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import Integer
from fastapi import Depends

from app.database import get_db
from app.models import User
from app.services.cookies import (
    set_auth_cookie,
    clear_auth_cookie,
    get_current_user_from_cookie,
    COOKIE_NAME,
)
from app.services.security import hash_password, verify_password, create_access_token
from app.services.templates import render

router = APIRouter(tags=["pages"], include_in_schema=False)


# ============================================
# Главная (лендинг)
# ============================================
@router.get("/")
def landing(request: Request):
    """Лендинг."""
    return render(request, "landing.html")


# ============================================
# Регистрация
# ============================================
@router.get("/register")
def register_form(request: Request):
    """Форма регистрации."""
    # Если уже залогинен — редирект на дашборд
    if get_current_user_from_cookie(request):
        return RedirectResponse("/dashboard", status_code=302)

    return render(request, "auth/register.html")


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Обработка формы регистрации."""
    # Проверяем, что email свободен
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return render(
            request,
            "auth/register.html",
            {
                "error": "Пользователь с таким email уже существует",
                "email": email,
            },
        )

    # Проверяем длину пароля
    if len(password) < 8:
        return render(
            request,
            "auth/register.html",
            {
                "error": "Пароль должен быть минимум 8 символов",
                "email": email,
            },
        )

    # Создаём пользователя
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Создаём токен
    token = create_access_token(subject=user.id)

    # Редирект на дашборд с установкой cookie
    response = RedirectResponse("/dashboard", status_code=302)
    set_auth_cookie(response, token)
    return response


# ============================================
# Логин
# ============================================
@router.get("/login")
def login_form(request: Request):
    """Форма логина."""
    if get_current_user_from_cookie(request):
        return RedirectResponse("/dashboard", status_code=302)

    return render(request, "auth/login.html")


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Обработка формы логина."""
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return render(
            request,
            "auth/login.html",
            {
                "error": "Неверный email или пароль",
                "email": email,
            },
        )

    if not user.is_active:
        return render(
            request,
            "auth/login.html",
            {
                "error": "Аккаунт деактивирован",
                "email": email,
            },
        )

    # Создаём токен
    token = create_access_token(subject=user.id)

    # Редирект на дашборд
    response = RedirectResponse("/dashboard", status_code=302)
    set_auth_cookie(response, token)
    return response


# ============================================
# Выход
# ============================================
@router.post("/auth/logout-web")
def logout_web(request: Request):
    """Выход из UI."""
    response = RedirectResponse("/", status_code=302)
    clear_auth_cookie(response)
    return response
# ============================================
# Дашборд
# ============================================
from sqlalchemy import func
from app.models import Monitor, Check


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    """Дашборд — список мониторов пользователя."""
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Получаем мониторы пользователя
    monitors = (
        db.query(Monitor)
        .filter(Monitor.user_id == user.id)
        .order_by(Monitor.created_at.desc())
        .all()
    )

    # Для каждого монитора — последняя проверка + статистика
    monitors_data = []
    for monitor in monitors:
        # Последняя проверка
        last_check = (
            db.query(Check)
            .filter(Check.monitor_id == monitor.id)
            .order_by(Check.checked_at.desc())
            .first()
        )

        # Статистика (uptime за всё время)
        stats = (
            db.query(
                func.count(Check.id).label("total"),
                func.sum(func.cast(Check.is_success, Integer)).label("successful"),
            )
            .filter(Check.monitor_id == monitor.id)
            .first()
        )

        total = stats.total or 0
        successful = stats.successful or 0
        uptime = round((successful / total * 100), 1) if total > 0 else None

        monitors_data.append({
            "monitor": monitor,
            "last_check": last_check,
            "uptime": uptime,
            "total_checks": total,
        })

    return render(
        request,
        "dashboard.html",
        {
            "monitors_data": monitors_data,
        },
    )


# ============================================
# Создание монитора (форма)
# ============================================
@router.post("/dashboard/monitors")
def create_monitor_web(
    request: Request,
    name: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(get_db),
):
    """Создание монитора через форму."""
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Валидация
    if not name.strip() or not url.strip():
        return RedirectResponse("/dashboard?error=empty", status_code=302)

    # Нормализуем URL
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    monitor = Monitor(
        user_id=user.id,
        name=name.strip(),
        url=url,
        check_interval=300,
        is_active=True,
    )
    db.add(monitor)
    db.commit()

    return RedirectResponse("/dashboard", status_code=302)


# ============================================
# Удаление монитора (форма)
# ============================================
@router.post("/dashboard/monitors/{monitor_id}/delete")
def delete_monitor_web(
    monitor_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Удаление монитора через форму."""
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == user.id)
        .first()
    )
    if monitor:
        db.delete(monitor)
        db.commit()

    return RedirectResponse("/dashboard", status_code=302)
# ============================================
# Детальная страница монитора
# ============================================
@router.get("/dashboard/monitors/{monitor_id}")
def monitor_detail(
    monitor_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Детальная страница монитора."""
    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    # Найти монитор
    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == user.id)
        .first()
    )
    if not monitor:
        return RedirectResponse("/dashboard", status_code=302)

    # Последние проверки
    checks = (
        db.query(Check)
        .filter(Check.monitor_id == monitor.id)
        .order_by(Check.checked_at.desc())
        .limit(50)
        .all()
    )

    # Статистика
    stats = (
        db.query(
            func.count(Check.id).label("total"),
            func.sum(func.cast(Check.is_success, Integer)).label("successful"),
            func.avg(Check.response_time_ms).label("avg_time"),
        )
        .filter(Check.monitor_id == monitor.id)
        .first()
    )

    total = stats.total or 0
    successful = stats.successful or 0
    failed = total - successful
    uptime = round((successful / total * 100), 1) if total > 0 else None

    return render(
        request,
        "monitor_detail.html",
        {
            "monitor": monitor,
            "checks": checks,
            "total": total,
            "successful": successful,
            "failed": failed,
            "uptime": uptime,
            "avg_time": round(float(stats.avg_time), 0) if stats.avg_time else None,
        },
    )


# ============================================
# Проверить монитор сейчас (форма)
# ============================================
@router.post("/dashboard/monitors/{monitor_id}/check-now")
async def check_now_web(
    monitor_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Ручная проверка монитора из UI."""
    from app.services.checker import check_url

    user = get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login", status_code=302)

    monitor = (
        db.query(Monitor)
        .filter(Monitor.id == monitor_id, Monitor.user_id == user.id)
        .first()
    )
    if not monitor:
        return RedirectResponse("/dashboard", status_code=302)

    # Проверка
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

    return RedirectResponse(
        f"/dashboard/monitors/{monitor_id}",
        status_code=302,
    )