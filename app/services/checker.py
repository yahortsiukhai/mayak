"""
Сервис проверки URL.

Делает HTTP-запрос и возвращает результат.
"""

import time

import httpx

from app.schemas.check import CheckResult


# ============================================
# Конфигурация проверки
# ============================================
DEFAULT_TIMEOUT = 10.0
USER_AGENT = "Mayak-Monitor/0.1 (+https://mayak.ru)"


async def check_url(url: str, timeout: float = DEFAULT_TIMEOUT) -> CheckResult:
    """
    Проверяет URL HTTP-запросом.

    Args:
        url: URL для проверки
        timeout: таймаут в секундах

    Returns:
        CheckResult с полями:
          - status_code: HTTP-код (или None)
          - response_time_ms: время в мс
          - is_success: True если 2xx/3xx
          - error: текст ошибки (или None)
    """
    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = await client.get(url)

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        # 2xx и 3xx — успех
        is_success = 200 <= response.status_code < 400

        return CheckResult(
            status_code=response.status_code,
            response_time_ms=elapsed_ms,
            is_success=is_success,
            error=None,
        )

    except httpx.TimeoutException:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            status_code=None,
            response_time_ms=elapsed_ms,
            is_success=False,
            error=f"Таймаут ({timeout} сек)",
        )

    except httpx.ConnectError as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            status_code=None,
            response_time_ms=elapsed_ms,
            is_success=False,
            error=f"Ошибка подключения: {e}",
        )

    except httpx.HTTPError as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            status_code=None,
            response_time_ms=elapsed_ms,
            is_success=False,
            error=f"HTTP-ошибка: {e}",
        )

    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return CheckResult(
            status_code=None,
            response_time_ms=elapsed_ms,
            is_success=False,
            error=f"Неизвестная ошибка: {e}",
        )