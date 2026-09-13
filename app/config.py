"""
Настройки приложения «Маяк».

Этот модуль читает переменные окружения из файла .env
и делает их доступными в коде как типизированный объект settings.

Использование:
    from app.config import settings
    print(settings.app_name)  # "Маяк"
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Все настройки приложения в одном классе.

    Pydantic автоматически:
      1. Читает переменные из файла .env
      2. Приводит их к нужному типу (str, bool, int)
      3. Проверяет, что обязательные поля заполнены
      4. Даёт значения по умолчанию, если переменная не задана
    """

    # Конфигурация Pydantic — откуда читать настройки
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ============================================
    # Приложение
    # ============================================
    app_name: str = "Маяк"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me"

        # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # ============================================
    # База данных
    # ============================================
    database_url: str = "postgresql+psycopg://mayak:mayak@localhost:5432/mayak"

    # ============================================
    # Redis
    # ============================================
    redis_url: str = "redis://localhost:6379/0"

    # ============================================
    # Telegram
    # ============================================
    telegram_bot_token: str = ""
    telegram_admin_chat_id: str = ""

    # ============================================
    # Email
    # ============================================
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""


# ============================================
# Готовый объект настроек
# ============================================
# Импортируй где угодно: from app.config import settings
settings = Settings()