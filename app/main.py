"""
Главный модуль приложения «Маяк».

Точка входа: создаётся FastAPI-приложение,
регистрируются роутеры, метрики, эндпоинты.
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

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


# ============================================
# Подключение роутеров
# ============================================
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitors.router)


# ============================================
# Метрики Prometheus
# ============================================
# Автоматически создаёт эндпоинт /metrics, который отдаёт:
#   - http_requests_total         (счётчик запросов)
#   - http_request_duration_seconds (время ответа, гистограмма)
#   - http_requests_in_progress    (запросы в обработке)
#
# Prometheus будет забирать эти метрики каждые 15 секунд.
# include_in_schema=False — скрываем /metrics из Swagger UI.
Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)


# ============================================
# Системные эндпоинты
# ============================================

@app.get("/", tags=["system"])
def root():
    """
    Главная страница — приветствие.
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
    Health-check — проверка, что сервис жив.

    Используется Kubernetes, балансировщиками, мониторингом.
    """
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }