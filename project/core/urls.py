from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import settings

from telegram_bot.views import TelegramWebhook
from tinkoff.views import TinkoffWebhook


urlpatterns = [
    path("admin/", admin.site.urls),
    path("webhook/", TelegramWebhook.as_view(), name="tg_webhook"),
    path("payhook/", TinkoffWebhook.as_view(), name="pay_webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)