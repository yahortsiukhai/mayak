"""
Работа с JWT-токеном в cookies.

Для UI мы храним токен в httpOnly-cookie (безопасно).
"""

from fastapi import Request, Response

from app.database import SessionLocal
from app.models import User
from app.services.security import decode_access_token


COOKIE_NAME = "mayak_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 дней


def set_auth_cookie(response: Response, token: str) -> None:
    """Устанавливает токен в httpOnly-cookie."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False,  # ⚠️ В проде — True (только HTTPS)
    )


def clear_auth_cookie(response: Response) -> None:
    """Удаляет cookie."""
    response.delete_cookie(COOKIE_NAME)


def get_current_user_from_cookie(request: Request) -> User | None:
    """
    Возвращает пользователя по токену из cookie.
    Возвращает None, если токена нет или он невалидный.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == int(user_id)).first()
    finally:
        db.close()
        