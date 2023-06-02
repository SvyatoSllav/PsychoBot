from django.contrib import admin
from django.db.models import Count, Q

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
        "users_amount",
        "users_who_bought_course_amount"
    )
    list_filter = ["user_id", "username", ]
    search_fields = ["user_id", "username", ]

    def users_amount(self, obj):
        return TelegramUser.objects.all().count()

    def users_who_bought_course_amount(self, obj):
        return TelegramUser.objects.filter(bought_course=True).count()

    users_amount.short_description = 'Количество подписанных'
    users_who_bought_course_amount.short_description = "Количество купивших курс"


@admin.register(Commands)
class CommandsAdmin(admin.ModelAdmin):
    list_display = (
        "cmd",
        "text",
    )
