"""
Регистрация всех моделей SQLAlchemy.
"""

from app.models.user import User
from app.models.monitor import Monitor
from app.models.check import Check

__all__ = ["User", "Monitor", "Check"]