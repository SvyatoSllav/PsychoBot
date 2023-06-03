from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telegram_bot.views import TelegramWebhook


class TinkoffWebhook(APIView):
    def post(self, request):
        try:
            logger.info(request.data)
            status = request.data["Status"]
            if status == "CONFIRMED":
                TelegramWebhook.confirmed_payment(request.data["OrderId"])
            if status == "REJECTED":
                TelegramWebhook.rejected_payment(request.data["OrderId"])
            return JsonResponse({"success": request.data})
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})
