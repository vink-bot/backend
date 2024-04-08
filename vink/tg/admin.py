"""Настройка отображения моделей телеграм бота в админ-панели."""

from django.contrib import admin
from .models import LastUpdate, OperatorChat, Operator, Invite


@admin.register(LastUpdate)
class LastUpdateAdmin(admin.ModelAdmin):
    """Настройка отображения LastUpdate модели  в админ-панели."""
    list_display = ("update_id",)


@admin.register(OperatorChat)
class OperatorChatAdmin(admin.ModelAdmin):
    """Настройка отображения OperatorChat модели в админ-панели."""
    list_display = (
        "operator",
        "chat_token",
        "date_create",
        "is_active",
        "status_verbose",
    )
    list_editable = ('is_active',)

    @admin.display(description="Статус")
    def status_verbose(self, object: OperatorChat):
        """Строковое свойство для представления поля статуса чата."""
        if object.is_active and object.token is not None:
            return "Активен"
        elif object.is_active and object.token is None:
            return "В ожидании клиента"
        elif object.is_active is False and object.token is not None:
            return "Завершен"
        return "Отключен"

    @admin.display(description="Токен пользователя")
    def chat_token(self, object: OperatorChat):
        chat_token = "-- НЕ НАЗНАЧЕН --"
        if object.token is not None:
            chat_token = object.token.chat_token
        return chat_token


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    """Настройка отображения модели Operator в админ-панели."""
    list_display = (
        "tg_user_id",
        "username",
        "first_name",
        "last_name",
        'is_enabled',
        "enabled_verbose",
    )
    list_editable = ('is_enabled',)

    @admin.display(description="Статус")
    def enabled_verbose(self, object: Operator):
        """Строковое представление для статуса подтверждения (is_enabled)."""
        if object.is_enabled:
            return "Подтвержден, работа в боте разрешена."
        return "Не подтвержден, работа в боте не разрешена."


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    """Настройка отображения модели Invite в админ-панели."""
    list_display = (
        "operator",
        "chat_token",
        "date_create",
        "is_active",
        "active_verbose",
    )
    list_editable = ('is_active',)

    @admin.display(description="Статус приглашения")
    def active_verbose(self, object: Invite):
        """Строковое свойство для представления поля is_active."""
        if object.is_active:
            return "Приглашение активно"
        return "Отменено"

    @admin.display(description="Токен пользователя")
    def chat_token(self, object: OperatorChat):
        chat_token = "-- НЕ НАЗНАЧЕН --"
        if object.token is not None:
            chat_token = object.token.chat_token
        return chat_token
