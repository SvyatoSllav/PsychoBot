from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telegram_bot.Tinkoff import TinkoffSimplePayment
from telegram_bot.loader import BOT
from telegram_bot.models import TelegramUser
from telegram_bot.views import TelegramWebhook


class TinkoffWebhook(APIView):
    def post(self, request):
        try:
            logger.info(request.data)
            status = request.data["Status"]
            if status == "CONFIRMED":
                TinkoffWebhook._confirmed_payment(request.data["OrderId"])
            if status == "REJECTED":
                TinkoffWebhook._rejected_payment(request.data["OrderId"])
            return JsonResponse({"success": request.data})
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})


    @classmethod
    def _confirmed_payment(cls, pk: str):
        """
        Посылает пользователю сообщение, что оплата прошла успешно и меняет статус в БД
        """
        try:
            user = TelegramWebhook._get_object_or_none(TelegramUser, id=id)
            user.bought_course = True
            user.save()
            BOT.send_message(chat_id=user.user_id, text="Оплата прошла успешно")
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})

    @classmethod
    def _rejected_payment(cls, id: str):
        """
        Посылает пользователю сообщение в случае непрошедшей оплаты и отправляет новую ссылку на повторную оплату
        """
        try:
            user = TelegramWebhook._get_object_or_none(TelegramUser, id=id)
            payment = TinkoffSimplePayment(terminal_id="1685039843752DEMO", password="jcw9vwrfgqx8fn0b")
            payment_result = payment.init(userid, "100", sign_request=True,
                                          notificationURL="https://8082-193-242-207-246.ngrok-free.app/payhook/",
                                          data={"Phone": "+79999999999"})
            payment_url = payment_result['PaymentURL']
            BOT.send_message(chat_id=user.user_id, text=f"Ошибка при оплате. Повторите попытку\n{payment_url}")
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})
