"""
Утилиты для работы с Jinja2-шаблонами.
"""

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates


# Путь к папке с шаблонами
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
STATIC_DIR = Path(__file__).parent.parent / "static"


# Jinja2-шаблоны
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def render(
    request: Request,
    template_name: str,
    context: dict | None = None,
):
    """
    Рендерит Jinja2-шаблон с общими переменными.

    Автоматически добавляет в контекст:
      - user: текущий пользователь (если есть)
    """
    from app.services.cookies import get_current_user_from_cookie

    user = get_current_user_from_cookie(request)

    ctx = {
        "request": request,
        "user": user,
        **(context or {}),
    }

    return templates.TemplateResponse(template_name, ctx)