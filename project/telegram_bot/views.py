from django.http import JsonResponse

from rest_framework.views import APIView

from .loader import BOT


class TelegramWebhook(APIView):
    def post(self, request):
        try:
            # TODO Добавить статус "Печатает"
            print(request.data)
            user_id = request.data.get("id").get("from").get("id")
            message = request.data.get("message").get("text")
            TelegramWebhook._handle_message(user_id=user_id, message=message)
            return JsonResponse({"success": True})
        except Exception as _exec:
            print(_exec)
            return JsonResponse({"Error": "Some error occured."})

    @classmethod
    def _handle_message(cls, user_id: int, message: str):
        if message == "/start":
            BOT.send_message(user_id, "Стартовое сообщение")
        elif message == "/help":
            BOT.send_message(user_id, "Хелповое сообщение")
        else:
            BOT.send_message(user_id, message)
