"""Настройка отображения моделей телеграм бота в админ-панели."""

from django.contrib import admin
from .models import LastUpdate, OperatorChat, Operator, Invite


class LastUpdateAdmin(admin.ModelAdmin):
    """Настройка отображения LastUpdate модели  в админ-панели."""
    list_display = (
        "update_id",
    )


admin.site.register(LastUpdate, LastUpdateAdmin)


class OperatorChatAdmin(admin.ModelAdmin):
    """Настройка отображения OperatorChat модели в админ-панели."""
    list_display = (
        "token",
        "operator",
        "date_create",
        "is_active",
        "status_verbose"
    )


admin.site.register(OperatorChat, OperatorChatAdmin)


class OperatorAdmin(admin.ModelAdmin):
    """Настройка отображения модели Operator в админ-панели."""
    list_display = (
        "tg_user_id",
        "full_name",
        "enabled_verbose",
    )


admin.site.register(Operator, OperatorAdmin)


class InviteAdmin(admin.ModelAdmin):
    """Настройка отображения модели Invite в админ-панели."""
    list_display = (
        "token",
        "operator",
        "date_create",
        "active_verbose",
    )


admin.site.register(Invite, InviteAdmin)
