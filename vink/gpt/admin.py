from django.contrib import admin

from .models import Message, Token, LastUpdate, ActiveOperator, OperatorChat


class TokenAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_token")


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "date_create",
        "token",
        "status",
        "user",
        "telegram_number_chat",
    )


admin.site.register(Token, TokenAdmin)
admin.site.register(Message, MessageAdmin)


class LastUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "update_id",
    )


admin.site.register(LastUpdate, LastUpdateAdmin)


class ActiveOperatorAdmin(admin.ModelAdmin):
    list_display = (
        "operator_user_id",
        "operator_chat_id",
    )


admin.site.register(ActiveOperator, ActiveOperatorAdmin)


class OperatorChatAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "operator_user_id",
        "operator_chat_id",
        "date_create",
        "is_active",
    )


admin.site.register(OperatorChat, OperatorChatAdmin)