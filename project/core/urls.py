from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import settings

from telegram_bot.views import TelegramWebhook

from tasks.views import get_status, run_task

urlpatterns = [
    path("admin/", admin.site.urls),
    path("webhook/", TelegramWebhook.as_view(), name="tg_webhook"),
    path("tasks/<task_id>/", get_status, name="get_status"),
    path("tasks/", run_task, name="run_task"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)