"""
Главный модуль приложения «Маяк».

Это точка входа: здесь создаётся FastAPI-приложение,
регистрируются эндпоинты и настраивается middleware.

Запуск:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.config import settings
from app.routers import auth, users, monitors


# ============================================
# Создание приложения
# ============================================
app = FastAPI(
    title=settings.app_name,
    description="Сервис мониторинга для малого бизнеса",
    version="0.1.0",
    debug=settings.debug,
)
# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitors.router)


# ============================================
# Системные эндпоинты
# ============================================

@app.get("/", tags=["system"])
def root():
    """
    Главная страница.

    Используется для проверки, что приложение живо.
    """
    return {
        "service": settings.app_name,
        "status": "ok",
        "message": "Ваш бизнес всегда на связи",
        "environment": settings.app_env,
    }


@app.get("/health", tags=["system"])
def health():
    """
    Health-check — проверка здоровья сервиса.

    Используется Kubernetes, балансировщиками и мониторингом.
    """
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }


@app.get("/metrics", tags=["system"])
def metrics():
    """
    Метрики в формате Prometheus.

    Prometheus будет регулярно забирать эти метрики
    и строить графики в Grafana.
    """
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )