import time
import pytz
from datetime import datetime
from timezonefinder import TimezoneFinder
from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telebot import types

from .loader import BOT

from .models import Commands, TelegramUser

from .utils import PaymentStatus


from .Tinkoff import TinkoffSimplePayment

class TelegramWebhook(APIView):
    def post(self, request):
        try:
            logger.info(request.data)

            if request.data.get("callback_query"):
                response_type = "callback_query"
                message = request.data.get(response_type).get("data")
            else:
                response_type = "message"
                message = request.data.get(response_type).get("text")

            user_id = request.data.get(response_type).get("from").get("id")
            username = request.data.get(response_type).get("from").get("username")
            location = request.data.get(response_type).get("location")

            TelegramUser.objects.get_or_create(
                user_id=user_id,
                username=username
            )
            if location:
                self._save_user_timezone(user_id=user_id, location=location)
            self._handle_message(user_id=user_id, message=message)
            return JsonResponse({"success": request.data})
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})

    @staticmethod
    def _handle_message(user_id: int, message: str):
        """
        Обрабатывает текст сообщения и исполняет соответствующее поведение
        """
        BOT.send_chat_action(chat_id=user_id, action="typing")
        # TODO Вернуть на проде
        # time.sleep(5)
        if message == "/start":
            TelegramWebhook._process_start_cmd(user_id=user_id)
        elif message == "/help":
            TelegramWebhook._process_help_cmd(user_id=user_id)
        elif message == "buy":
            TelegramWebhook._process_payment_cmd(user_id=user_id)
        elif message:
            # TODO: Обработка ответов.
            # TODO: 1) Условие на то, что курс куплен
            # TODO: 2) Создание объекта сообщения с привязкой к задаче и юзеру
            # TODO: 3) Если сообщение ответ уже создано, не сохранять его вновь
            # TODO: 4) Если сообщений ожидается несколько, считать их в Message
            # TODO: 5) Проверять, достаточно ли сообщений сохранено в таске
            BOT.send_message(user_id, f"Ваше сообщение {message}")

    @classmethod
    def _process_start_cmd(cls, user_id: int):
        """
        Обрабатывает команду /start.
        """
        # TODO поменять условие, сначал проверять локацию если нет, добваить клавиатуру
        keyboard = types.ReplyKeyboardMarkup(
            row_width=1,
            resize_keyboard=True
        )
        inlinekeyboard = types.InlineKeyboardMarkup(
            row_width=1
        )
        inlinekeyboard.add(types.InlineKeyboardButton("Оплатить", callback_data="buy"))
        button_geo = types.KeyboardButton(
            text="Отправить местоположение",
            request_location=True
        )
        keyboard.add(button_geo)
        user = TelegramUser.objects.get(user_id=user_id)
        if user.timezone:
            keyboard = types.ReplyKeyboardRemove()
        start_cmd_text = Commands.objects.filter(cmd="/start")
        if start_cmd_text.exists():
            BOT.send_message(
                user_id,
                start_cmd_text[0].text,
                reply_markup=keyboard
            )
            BOT.send_message(
                user_id,
                start_cmd_text[0].text,
                reply_markup=inlinekeyboard
            )
            return
        BOT.send_message(
            user_id,
            "Стартовое сообщение",
            reply_markup=keyboard
        )
        BOT.send_message(
            user_id,
            "Необходимо оплатить курс",
            reply_markup=inlinekeyboard
        )

    @classmethod
    def _process_help_cmd(cls, user_id):
        """
        Обрабатывает команду /help
        """
        start_cmd_text = Commands.objects.filter(cmd="/help")
        if start_cmd_text.exists():
            BOT.send_message(user_id, start_cmd_text[0].text)
            return
        BOT.send_message(user_id, "Хелповое сообщение")

    @classmethod
    def _process_payment_cmd(cls, user_id):
        payment = TinkoffSimplePayment(terminal_id="1685039843752DEMO", password="jcw9vwrfgqx8fn0b")
        user = TelegramUser.objects.get(
            user_id=user_id,
        )
        try:
            payment_result = payment.init(user.order_id, "100", sign_request=True, notificationURL="https://2100-5-16-122-1.ngrok-free.app/payhook/", data={"Phone": "+79999999999"})
            payment_url = payment_result['PaymentURL']
            BOT.send_message(user_id, f"Оплатите курс по этой ссылке: {payment_url}")
            user.payment_status = PaymentStatus.NEW
            logger.info(user)
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "error during payment"})





    @staticmethod
    def _save_user_timezone(user_id: int, location: dict[str, int]):
        """
        Обновляет временную зону пользователя.
        """
        timezone = TimezoneFinder().timezone_at(
            lng=location["longitude"],
            lat=location["latitude"]
        )
        user = TelegramUser.objects.get(user_id=user_id)
        user.timezone = timezone
        user.save()
        BOT.send_chat_action(chat_id=user_id, action="typing")
        # TODO Вернуть на проде
        # time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text="Благодарим за доверие",
            reply_markup=types.ReplyKeyboardRemove()
        )
        # TODO Для селери
        # timenow = datetime.now(tz)
