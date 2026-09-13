"""
Эндпоинты для работы с пользователями.
"""

from fastapi import APIRouter, Depends

from app.models import User
from app.schemas.user import UserRead
from app.services.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Возвращает данные текущего авторизованного пользователя."""
    return current_user
    