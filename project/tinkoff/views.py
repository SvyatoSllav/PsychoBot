from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telegram_bot.Tinkoff import TinkoffSimplePayment
from telegram_bot.consts import messages_const
from telegram_bot.loader import BOT
from telegram_bot.models import TelegramUser
from telegram_bot.views import TelegramWebhook
from telegram_bot.keyboards import get_buy_keyboard

from core import settings


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
            user.bought_course = True
            user.save()
            BOT.send_message(chat_id=user.user_id, text="Оплата прошла успешно")
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})

    @classmethod
    def _rejected_payment(cls, pk: str):
        """
        Посылает пользователю сообщение в случае непрошедшей оплаты
        и отправляет новую ссылку на повторную оплату
        """
        try:
            user = TelegramWebhook._get_object_or_none(TelegramUser, id=pk)
            payment = TinkoffSimplePayment(terminal_id=settings.TERMINAL_KEY,
                                           password=settings.PASSWORD)
            payment_result = payment.init(pk, settings.AMOUNT, sign_request=True,
                                          notificationURL=settings.NOTIFICATION_URL,
                                          data={"Phone": user.phone})
            payment_url = payment_result['PaymentURL']
            buy_keyboard = get_buy_keyboard(payment_url)

            BOT.send_message(
                user.user_id,
                text=messages_const.ERROR_DURING_PAYMENT,
                reply_markup=buy_keyboard)
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})
