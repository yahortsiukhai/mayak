"""
UI-роутер: отдаёт HTML-страницы.
"""

from fastapi import APIRouter, Request

from app.services.templates import render

router = APIRouter(tags=["pages"])


@router.get("/", include_in_schema=False)
def landing(request: Request):
    """Лендинг — публичная страница."""
    return render(request, "landing.html")