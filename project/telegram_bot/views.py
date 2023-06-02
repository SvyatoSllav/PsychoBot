import time
from timezonefinder import TimezoneFinder
from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telebot import types

from psycho_survey.models import Task, Messages

from .loader import BOT
from .models import Commands, TelegramUser
from .keyboards import get_location_btn
from .utils import get_active_task


class TelegramWebhook(APIView):
    def post(self, request):
        try:
            logger.info(request.data)
            user_id = request.data.get("message").get("from").get("id")
            message = request.data.get("message").get("text")
            username = request.data.get("message").get("from").get("username")
            location = request.data.get("message").get("location")
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
        elif message:
            return TelegramWebhook._proccess_undefined_message(
                user_id=user_id, message=message
            )

    @classmethod
    def _process_start_cmd(cls, user_id: int):
        """
        Обрабатывает команду /start.
        """
        user = TelegramUser.objects.get(user_id=user_id)
        keyboard = types.ReplyKeyboardRemove()
        if not user.timezone:
            keyboard = get_location_btn()
        start_cmd_text = Commands.objects.filter(cmd="/start")
        if start_cmd_text.exists():
            BOT.send_message(
                user_id,
                start_cmd_text[0].text,
                reply_markup=keyboard
            )
            return
        BOT.send_message(
            user_id,
            "Стартовое сообщение",
            reply_markup=keyboard,
        )

    @classmethod
    def _process_help_cmd(cls, user_id):
        """
        Обрабатывает команду /help
        """
        logger.info(f"{Task.objects.filter(id=1)}")
        start_cmd_text = Commands.objects.filter(cmd="/help")
        if start_cmd_text.exists():
            BOT.send_message(user_id, start_cmd_text[0].text)
            return
        BOT.send_message(user_id, "Хелповое сообщение")

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
        time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text="Благодарим за доверие",
            reply_markup=types.ReplyKeyboardRemove()
        )

    @classmethod
    def _proccess_undefined_message(cls, user_id: int, message: str):
        """
        Обрабатывает неопределенное сообщение.
        """
        try:
            # TODO Поменять ветвление на валидирующие функции из класса предка
            user = TelegramUser.objects.get(user_id=user_id)
            task = get_active_task(day_number=user.day_number)
            latest_msg_msg_count = 0
            if Messages.objects.filter(user=user).exists():
                latest_msg_msg_count = Messages.objects.latest("created_at").msg_count
            # Если курс не куплен, то отрабатываем как старт
            if not user.bought_course:
                TelegramWebhook._process_start_cmd(user_id=user_id)
            if not user.timezone:
                # Если нет таймзоны, запрашиваем местоположение
                BOT.send_chat_action(chat_id=user_id, action="typing")
                time.sleep(5)
                BOT.send_message(
                    chat_id=user_id,
                    text="Для того, чтобы начать курс, отправьте ваше местоположение. (Нажмите на кнопку внизу клавиатуры)",
                    reply_markup=get_location_btn()
                )
                return
            if user.task_sent:
                # Если сообщение уже отправлено
                BOT.send_chat_action(chat_id=user_id, action="typing")
                time.sleep(5)
                BOT.send_message(
                    chat_id=user_id,
                    text="Благодарим вас, вы уже выполнили сегодняшнее задание"
                )
                return
            if not task.is_answer_counted_task:
                Messages.objects.create(
                    user=user,
                    task=task,
                    message_text=message,
                )
                user.task_sent = True
                user.save()
                return user
            if task.amount_of_message != latest_msg_msg_count:
                incemented_latest_msg_count = latest_msg_msg_count + 1
                return Messages.objects.create(
                    user=user,
                    task=task,
                    message_text=message,
                    msg_count=incemented_latest_msg_count,
                )
            user.task_sent = True
            user.save()
            BOT.send_chat_action(chat_id=user_id, action="typing")
            time.sleep(5)
            BOT.send_message(
                chat_id=user_id,
                text="Благодарим вас, вы уже выполнили сегодняшнее задание"
            )
            return user
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": "Some error occured."})
