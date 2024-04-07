"""Модуль настройки приложения TG."""

from django.apps import AppConfig


class TgConfig(AppConfig):
    """Класс настройки приложения TG."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tg'
    verbose_name = 'Операторы'
