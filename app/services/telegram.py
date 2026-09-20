"""
Сервис отправки сообщений в Telegram.

Использует httpx для асинхронных запросов к Bot API.
"""

import logging

import httpx

from app.config import settings


logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


async def send_message(
    chat_id: str | int,
    text: str,
    parse_mode: str = "HTML",
) -> bool:
    """
    Отправляет сообщение в Telegram.

    Args:
        chat_id: ID чата (куда отправить)
        text: текст сообщения (поддерживает HTML)
        parse_mode: HTML или Markdown

    Returns:
        True если успешно, False при ошибке.
    """
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN не установлен — пропускаем отправку")
        return False

    url = TELEGRAM_API_URL.format(token=settings.telegram_bot_token)

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                logger.info(f"Telegram: сообщение отправлено в {chat_id}")
                return True
            else:
                logger.error(
                    f"Telegram API error: {response.status_code} — {response.text}"
                )
                return False

    except httpx.HTTPError as e:
        logger.error(f"Telegram: ошибка HTTP — {e}")
        return False
    except Exception as e:
        logger.error(f"Telegram: неизвестная ошибка — {e}")
        return False


# ============================================
# Готовые шаблоны сообщений
# ============================================

def format_down_alert(monitor_name: str, url: str, error: str) -> str:
    """Сообщение о падении монитора."""
    return (
        f"🔴 <b>ВНИМАНИЕ</b>\n\n"
        f"<b>{monitor_name}</b> не работает!\n"
        f"🌐 URL: <code>{url}</code>\n"
        f"⚠️ Причина: {error}\n\n"
        f"<b>Что делать:</b>\n"
        f"1. Проверьте хостинг\n"
        f"2. Не закончился ли домен\n"
        f"3. Не истёк ли SSL-сертификат\n"
        f"4. Свяжитесь с разработчиком"
    )


def format_up_alert(monitor_name: str) -> str:
    """Сообщение о восстановлении."""
    return (
        f"🟢 <b>Восстановлено</b>\n\n"
        f"<b>{monitor_name}</b> снова работает.\n"
        f"Всё в порядке 👍"
    )


def format_test_message() -> str:
    """Тестовое сообщение."""
    return (
        "✅ <b>Маяк подключён</b>\n\n"
        "Теперь вы будете получать уведомления о падении сайтов.\n\n"
        "<i>Это тестовое сообщение.</i>"
    )
# ============================================
# Polling: получение обновлений от Telegram
# ============================================
async def get_updates(offset: int | None = None, timeout: int = 5) -> list[dict]:
    """
    Получает новые сообщения от Telegram (long polling).

    Args:
        offset: ID последнего обработанного апдейта (чтобы не получать повторно)
        timeout: таймаут long polling

    Returns:
        Список апдейтов.
    """
    if not settings.telegram_bot_token:
        return []

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"

    params = {
        "timeout": timeout,
        "allowed_updates": ["message"],
    }
    if offset:
        params["offset"] = offset

    try:
        async with httpx.AsyncClient(timeout=timeout + 5) as client:
            response = await client.get(url, params=params)
            data = response.json()

            if not data.get("ok"):
                logger.error(f"Telegram getUpdates error: {data}")
                return []

            return data.get("result", [])

    except Exception as e:
        logger.error(f"Telegram getUpdates exception: {e}")
        return []


async def send_welcome_after_link(chat_id: int, user_email: str) -> None:
    """Отправляет приветствие после успешной привязки."""
    text = (
        f"✅ <b>Маяк подключён!</b>\n\n"
        f"Аккаунт: <code>{user_email}</code>\n\n"
        f"Теперь вы будете получать уведомления о падении сайтов.\n\n"
        f"<i>Проверьте работу настройки — я пришлю тестовое сообщение.</i>"
    )
    await send_message(chat_id, text)


async def send_invalid_token_message(chat_id: int) -> None:
    """Сообщение, если токен не найден."""
    text = (
        "❌ <b>Не удалось привязать</b>\n\n"
        "Ссылка недействительна или устарела.\n\n"
        "Вернитесь на сайт и попробуйте снова."
    )
    await send_message(chat_id, text)
# ============================================
# Polling: получение обновлений от Telegram
# ============================================
async def get_updates(offset: int | None = None, timeout: int = 5) -> list[dict]:
    """Получает новые сообщения от Telegram (long polling)."""
    if not settings.telegram_bot_token:
        return []

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"

    params = {
        "timeout": timeout,
        "allowed_updates": ["message"],
    }
    if offset:
        params["offset"] = offset

    try:
        async with httpx.AsyncClient(timeout=timeout + 5) as client:
            response = await client.get(url, params=params)
            data = response.json()

            if not data.get("ok"):
                logger.error(f"Telegram getUpdates error: {data}")
                return []

            return data.get("result", [])

    except Exception as e:
        logger.error(f"Telegram getUpdates exception: {e}")
        return []


async def send_welcome_after_link(chat_id: int, user_email: str) -> None:
    """Отправляет приветствие после успешной привязки."""
    text = (
        f"✅ <b>Маяк подключён!</b>\n\n"
        f"Аккаунт: <code>{user_email}</code>\n\n"
        f"Теперь вы будете получать уведомления о падении сайтов.\n\n"
        f"<i>Проверьте работу настройки — я пришлю тестовое сообщение.</i>"
    )
    await send_message(chat_id, text)


async def send_invalid_token_message(chat_id: int) -> None:
    """Сообщение, если токен не найден."""
    text = (
        "❌ <b>Не удалось привязать</b>\n\n"
        "Ссылка недействительна или устарела.\n\n"
        "Вернитесь на сайт и попробуйте снова."
    )
    await send_message(chat_id, text)