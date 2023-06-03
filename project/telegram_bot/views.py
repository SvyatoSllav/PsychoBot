import time
from timezonefinder import TimezoneFinder
from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telebot import types

from psycho_survey.models import Review

from .loader import BOT
from .models import Commands, TelegramUser
from .keyboards import get_loc_and_phone_keyboard
from .utils import get_active_task
from .mixins.mixins import ValidatorsMixin, MessageHandlers
from .consts import messages_const
from .consts import error_const


class TelegramWebhook(ValidatorsMixin, MessageHandlers, APIView):
    def post(self, request):
        try:
            logger.info(request.data)
            user_id = request.data.get("message").get("from").get("id")
            message = request.data.get("message").get("text")
            username = request.data.get("message").get("from").get("username")
            location = request.data.get("message").get("location")
            contact = request.data.get("message").get("contact")
            TelegramUser.objects.get_or_create(
                user_id=user_id,
                username=username
            )
            if location:
                return self._save_user_timezone(
                    user_id=user_id,
                    location=location
                )
            if contact:
                return self._save_user_phone(
                    user_id=user_id,
                    phone=contact.get("phone_number")
                )
            self._handle_message(user_id=user_id, message=message)
            return JsonResponse({"success": request.data})
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": error_const.UNEXPECTED_ERROR_MSG})

    @staticmethod
    def _handle_message(user_id: int, message: str):
        """
        Обрабатывает текст сообщения и исполняет соответствующее поведение
        """
        BOT.send_chat_action(chat_id=user_id, action="typing")
        time.sleep(5)
        if message == "/start":
            TelegramWebhook._process_start_cmd(user_id=user_id)
        elif message == "/help":
            TelegramWebhook._process_help_cmd(user_id=user_id)
        elif message:
            TelegramWebhook._proccess_undefined_message(
                user_id=user_id, message=message
            )

    @classmethod
    def _process_start_cmd(cls, user_id: int):
        """
        Обрабатывает команду /start.
        """
        # TODO: Зарпрашивать локацию и номер телефона черзе TelegramWebhook._ask_for_location
        # TODO: Вынести в миксин по обработке стартовой команды
        user = TelegramWebhook._get_object_or_none(
            TelegramUser,
            user_id=user_id
        )
        keyboard = get_loc_and_phone_keyboard(user=user)
        contact_saved = user.timezone and user.phone
        if contact_saved:
            keyboard = types.ReplyKeyboardRemove()
        start_cmd_text = Commands.objects.filter(cmd="/start")
        if start_cmd_text.exists():
            BOT.send_message(
                user_id,
                start_cmd_text[0].text,
                reply_markup=keyboard
            )
            if not contact_saved:
                TelegramWebhook._ask_for_location(user_id=user.user_id)
            else:
                BOT.send_message(
                    user_id,
                    text=messages_const.COURSE_STARTED,
                    reply_markup=keyboard,
                )
            return
        BOT.send_message(
            user_id,
            "Стартовое сообщение",
            reply_markup=keyboard,
        )
        if not contact_saved:
            TelegramWebhook._ask_for_location(user_id=user.user_id)
        else:
            BOT.send_message(
                user_id,
                text=messages_const.COURSE_STARTED,
                reply_markup=keyboard,
            )

    @classmethod
    def _process_help_cmd(cls, user_id):
        """
        Обрабатывает команду /help
        """
        # TODO Вынести в миксины
        start_cmd_text = TelegramWebhook._get_object_or_none(
            Commands,
            cmd="/help"
        )
        if start_cmd_text:
            BOT.send_message(user_id, start_cmd_text.text)
            return
        BOT.send_message(user_id, "Хелповое сообщение")

    @classmethod
    def _proccess_undefined_message(cls, user_id: int, message: str):
        """
        Обрабатывает неопределенное сообщение.
        """
        try:
            # TODO Поменять ветвление на валидирующие функции из класса предка
            user = TelegramUser.objects.get(user_id=user_id)
            task = get_active_task(day_number=user.day_number)
            review_exists = TelegramWebhook._get_object_or_none(
                Review,
                user=user
            )
            task_msg_count = TelegramWebhook._get_latest_message_or_zero(
                user=user
            )
            # Если курс не куплен, то отрабатываем как старт
            if not user.bought_course:
                return TelegramWebhook._process_start_cmd(user_id=user_id)
            # Сценарий если отзыв существует
            if review_exists:
                return TelegramWebhook._handle_review_exists_scenario(
                    user_id=user_id
                )
            # Если нет таймзоны, запрашиваем местоположение
            if not user.timezone or not user.phone:
                return TelegramWebhook._ask_for_location_and_phone(
                    user_id=user_id
                )
            if user.task_sent:
                # Если ответ на сообщение отправлен
                return TelegramWebhook._task_completed_scenario(
                    user=user,
                    message=message
                )
            # Если таск с подсчетом сообщений и сообщение всё еще ожидается
            waiting_for_msgs = TelegramWebhook._is_waiting_for_msgs(
                task=task,
                task_msg_count=task_msg_count
            )
            is_finall_msg_of_task = TelegramWebhook._is_task_finall_msg(
                task=task,
                task_msg_count=task_msg_count
            )
            if waiting_for_msgs:
                return TelegramWebhook._wait_for_msgs(
                    user=user,
                    task=task,
                    message=message,
                    task_msg_count=task_msg_count
                )
            elif is_finall_msg_of_task:
                TelegramWebhook._save_finall_msg(user_id=user_id)
            user.task_sent = True
            user.save()
            if user.day_number == 10 and not review_exists:
                return TelegramWebhook._save_review(user=user, message=message)
            TelegramWebhook._handle_task_message(
                user=user,
                task=task,
                message=message
                )
        except Exception as _exec:
            logger.error(f"{_exec}")
            return JsonResponse({"Error": error_const.UNEXPECTED_ERROR_MSG})

    # TODO Вынести в миксины
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
            text=messages_const.GRATITUDE_FOR_LOCATION_OR_PHONE,
            reply_markup=types.ReplyKeyboardRemove()
        )

    # TODO Вынести в миксины
    @staticmethod
    def _save_user_phone(user_id: int, phone: str):
        """
        Обновляет телефон пользователя.
        """
        user = TelegramUser.objects.get(user_id=user_id)
        user.phone = phone
        user.save()
        BOT.send_chat_action(chat_id=user_id, action="typing")
        time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text=messages_const.GRATITUDE_FOR_LOCATION_OR_PHONE,
            reply_markup=types.ReplyKeyboardRemove()
        )

