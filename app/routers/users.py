"""
Эндпоинты для работы с пользователями.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserRead
from app.services.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


# ============================================
# Схемы
# ============================================
class TelegramLinkRequest(BaseModel):
    """Запрос на привязку Telegram."""
    chat_id: str


# ============================================
# Эндпоинты
# ============================================
@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Возвращает данные текущего пользователя."""
    return current_user


@router.post("/me/telegram", response_model=UserRead)
def link_telegram(
    data: TelegramLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Привязывает Telegram chat_id к пользователю."""
    current_user.telegram_chat_id = data.chat_id
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/telegram/test")
async def test_telegram(
    current_user: User = Depends(get_current_user),
):
    """Отправляет тестовое сообщение в Telegram."""
    from app.services.telegram import send_message, format_test_message

    if not current_user.telegram_chat_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала привяжите Telegram",
        )

    success = await send_message(
        current_user.telegram_chat_id,
        format_test_message(),
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось отправить сообщение",
        )

    return {"status": "sent"}


@router.delete("/me/telegram", status_code=status.HTTP_204_NO_CONTENT)
def unlink_telegram(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отвязывает Telegram от пользователя."""
    current_user.telegram_chat_id = None
    db.commit()
    return None