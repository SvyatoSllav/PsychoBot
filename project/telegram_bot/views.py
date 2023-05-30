from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from .loader import BOT


class TelegramWebhook(APIView):
    def post(self, request):
        try:
            # TODO Добавить статус "Печатает"
            logger.info(request.data)
            for key, value in request.data.items():
                logger.info(key, value, "FDLS")
            user_id = request.data.get("message").get("from").get("id")
            message = request.data.get("message").get("text")
            TelegramWebhook._handle_message(user_id=user_id, message=message)
            return JsonResponse({"success": request.data})
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occurmessageed."})

    @classmethod
    def _handle_message(cls, user_id: int, message: str):
        if message == "/start":
            BOT.send_message(user_id, "Стартовое сообщение")
        elif message == "/help":
            BOT.send_message(user_id, "Хелповое сообщение")
        else:
            BOT.send_message(user_id, message)
