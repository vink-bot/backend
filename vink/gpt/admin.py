from django.contrib import admin

from .models import Message, Token


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
        "recipient"
    )


admin.site.register(Token, TokenAdmin)
admin.site.register(Message, MessageAdmin)


