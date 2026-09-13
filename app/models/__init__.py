"""
Регистрация всех моделей SQLAlchemy.

Импортируй сюда каждую модель — Alembic будет видеть их
при создании миграций.
"""

from app.models.user import User

__all__ = ["User"]