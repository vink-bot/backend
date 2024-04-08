"""Модуль настройки приложения GPT."""

from django.apps import AppConfig


class GptConfig(AppConfig):
    """Класс настройки приложения GPT."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "gpt"
    verbose_name = "GPT чат"
