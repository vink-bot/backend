from django.contrib import admin
from .models import LastUpdate, OperatorChat, Operator, Invite


class LastUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "update_id",
    )


admin.site.register(LastUpdate, LastUpdateAdmin)


class OperatorChatAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "operator",
        "date_create",
        "is_active",
    )


admin.site.register(OperatorChat, OperatorChatAdmin)


class OperatorAdmin(admin.ModelAdmin):
    list_display = (
        "tg_user_id",
        "first_name",
        "last_name",
        "username",
        "is_enabled",
    )


admin.site.register(Operator, OperatorAdmin)


class InviteAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "operator",
        "date_create",
        "is_active",
    )


admin.site.register(Invite, InviteAdmin)
