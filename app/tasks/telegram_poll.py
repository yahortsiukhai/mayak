"""
Celery-задача для polling Telegram.

Каждые 5 секунд проверяет новые сообщения боту.
Обрабатывает команду /start TOKEN — привязывает chat_id к пользователю.
"""

import asyncio
import logging
import secrets

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import User
from app.services.telegram import (
    get_updates,
    send_welcome_after_link,
    send_invalid_token_message,
    send_message,
)


logger = logging.getLogger(__name__)

# Храним offset между запусками
_last_offset: int | None = None


def generate_link_token() -> str:
    """Генерирует безопасный одноразовый токен."""
    return secrets.token_urlsafe(24)


@celery_app.task(name="app.tasks.telegram_poll.poll_updates")
def poll_updates() -> dict:
    """
    Polling-задача: получает новые сообщения от Telegram.
    """
    global _last_offset

    updates = asyncio.run(get_updates(offset=_last_offset, timeout=5))

    if not updates:
        return {"processed": 0}

    processed = 0

    for update in updates:
        update_id = update.get("update_id")
        if update_id:
            _last_offset = update_id + 1

        message = update.get("message")
        if not message:
            continue

        text = message.get("text", "").strip()
        chat_id = message.get("chat", {}).get("id")

        if not chat_id:
            continue

        if text.startswith("/start"):
            parts = text.split(maxsplit=1)
            token = parts[1].strip() if len(parts) > 1 else None

            if token:
                db = SessionLocal()
                try:
                    user = (
                        db.query(User)
                        .filter(User.telegram_link_token == token)
                        .first()
                    )

                    if user:
                        user.telegram_chat_id = str(chat_id)
                        user.telegram_link_token = None
                        db.commit()

                        asyncio.run(send_welcome_after_link(chat_id, user.email))
                        logger.info(f"Telegram linked: user={user.id}, chat_id={chat_id}")
                    else:
                        asyncio.run(send_invalid_token_message(chat_id))
                        logger.warning(f"Invalid token: {token}")

                finally:
                    db.close()
            else:
                asyncio.run(send_message(
                    chat_id,
                    "👋 Привет! Чтобы привязать аккаунт — перейдите в <b>Настройки</b> "
                    "на сайте Маяка и нажмите <b>«Привязать Telegram»</b>."
                ))

            processed += 1

    return {"processed": processed}