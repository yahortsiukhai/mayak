"""
Главный модуль приложения «Маяк».
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.routers import auth, users, monitors, pages


app = FastAPI(
    title=settings.app_name,
    description="Сервис мониторинга для малого бизнеса",
    version="0.1.0",
    debug=settings.debug,
)

# Роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(monitors.router)
app.include_router(pages.router)

# Метрики
Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)

# Статика
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "healthy",
        "environment": settings.app_env,
    }