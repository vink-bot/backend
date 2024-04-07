from django.contrib import admin

from .models import Message, Token
from tg.models import Operator


class TokenAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_token")


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "date_create",
        "chat_token",
        "status_verbose",
        "user",
        "operator_verbose",
        "recipient"
    )
    
    @admin.display(description="Токен пользователя")
    def chat_token(self, object: Message):
        chat_token = ""
        if object.token is not None:
            chat_token = object.token.chat_token
        return chat_token
    
    @admin.display(description="Статус доставки")
    def status_verbose(self, object: Message):
        if object.user == "USER":
            if object.is_handled:
                return "Доставлено"
            else:
                return "Ожидает"
        else:        
            if object.status == "0":
                return "Ожидает"
            elif object.status == "1":
                return "Доставлено"
        return "Отмена"
    
    @admin.display(description="Оператор")
    def operator_verbose(self, object: Message):
        operator: Operator = Operator.objects.filter(
            tg_user_id=object.telegram_number_chat).first()
        if operator is not None:
            return operator.full_name
        return "-"

admin.site.register(Token, TokenAdmin)
admin.site.register(Message, MessageAdmin)


