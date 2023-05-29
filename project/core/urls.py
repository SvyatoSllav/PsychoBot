from django.contrib import admin
from django.urls import path

from telegram_bot.views import TelegramWebhook

from tasks.views import get_status, home, run_task

urlpatterns = [
    path("admin/", admin.site.urls),
    path("webhook/", TelegramWebhook.as_view(), name="tg_webhook"),
    path("tasks/<task_id>/", get_status, name="get_status"),
    path("tasks/", run_task, name="run_task"),
    path("", home, name="home"),
]
