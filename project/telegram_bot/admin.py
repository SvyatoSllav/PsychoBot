from django.contrib import admin
from .models import TelegramUser, Commands


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "username",
        "day_number",
        "bought_course",
        "task_sent",
        "timezone",
    )


@admin.register(Commands)
class CommandsAdmin(admin.ModelAdmin):
    list_display = (
        "cmd",
        "text",
    )
