from django.contrib import admin

from .models import Message, Token


class TokenAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_token")


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text_responce",
        "text_request",
        "date_responce",
        "date_request",
        "author",
    )


admin.site.register(Token, TokenAdmin)
admin.site.register(Message, MessageAdmin)
