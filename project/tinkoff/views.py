from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from core import settings

from telegram_bot.Tinkoff import TinkoffSimplePayment
from telegram_bot.loader import BOT
from telegram_bot.models import TelegramUser
from telegram_bot.views import TelegramWebhook

from telegram_bot.consts import messages_const


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
        Посылает пользователю сообщение, что оплата прошла успешно
        и меняет статус в БД
        """
        try:
            user = TelegramWebhook._get_object_or_none(TelegramUser, id=pk)
            logger.info(pk)
            user.bought_course = True
            user.save()
            BOT.send_message(
                chat_id=user.user_id,
                text=messages_const.PAYEMENT_IS_DONE
            )
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})

    @classmethod
    def _rejected_payment(cls, id: str):
        """
        Посылает пользователю сообщение в случае непрошедшей оплаты
        и отправляет новую ссылку на повторную оплату
        """
        try:
            user = TelegramWebhook._get_object_or_none(TelegramUser, id=id)
            payment = TinkoffSimplePayment(terminal_id=settings.TERMINAL_KEY,
                                           password=settings.PASSWORD)
            payment_result = payment.init(id, settings.AMOUNT, sign_request=True,
                                          notificationURL=settings.NOTIFICATION_URL,
                                          data={"Phone": user.phone})
            payment_url = payment_result['PaymentURL']
            BOT.send_message(chat_id=user.user_id,
                             text=f"Ошибка при оплате. Повторите попытку\n{payment_url}")
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})
