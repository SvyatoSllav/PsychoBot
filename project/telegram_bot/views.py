import time

from django.http import JsonResponse

from rest_framework.views import APIView
from loguru import logger

from telebot import types

from psycho_survey.models import Review

from .loader import BOT
from .models import Commands, TelegramUser
from .keyboards import get_loc_and_phone_keyboard, get_buy_keyboard
from .utils import get_active_task, get_payment_url
from .mixins.mixins import ValidatorsMixin, MessageHandlers
from .consts import messages_const
from .consts import error_const


class TelegramWebhook(ValidatorsMixin, MessageHandlers, APIView):
    def post(self, request):
        try:
            logger.info(request.data)
            if request.data.get("callback_query"):
                response_type = "callback_query"
                message = request.data.get(response_type, dict()).get("data")
            else:
                response_type = "message"
                message = request.data.get(response_type, dict()).get("text")

            user_id = request.data.get(response_type, dict()).get("from", {}).get("id")
            username = request.data.get(response_type, dict()).get("from", {}).get("username")
            location = request.data.get(response_type, dict()).get("location")
            contact = request.data.get("message", dict()).get("contact")
            user = TelegramUser.objects.get_or_create(
                user_id=user_id,
                username=username
            )[0]
            if location and not user.timezone:
                self._save_user_timezone(
                    user_id=user_id,
                    location=location
                )
                return JsonResponse({"status": "Success"})
            if contact and not user.phone:
                self._save_user_phone(
                    user_id=user_id,
                    phone=contact.get("phone_number")
                )
                return JsonResponse({"status": "Success"})
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
        logger.info(message)
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
        user = TelegramWebhook._get_object_or_none(
            TelegramUser,
            user_id=user_id
        )
        loc_and_phone_keyboard = get_loc_and_phone_keyboard(user=user)
        if not user.phone:
            return BOT.send_message(
                user_id,
                text=messages_const.ASK_FOR_PHONE,
                reply_markup=loc_and_phone_keyboard
            )
        buy_keyboard = get_buy_keyboard(get_payment_url(user))
        contact_saved = user.timezone and user.phone
        start_cmd_text = TelegramWebhook._get_object_or_none(
            Commands,
            cmd="/start"
        )
        message_text = messages_const.COURSE_STARTED
        if start_cmd_text:
            message_text = start_cmd_text.text
        if not user.bought_course:
            return BOT.send_message(
                user_id,
                text=messages_const.COURSE_IS_NOT_BOUGHT,
                reply_markup=buy_keyboard
            )
        if not contact_saved:
            return TelegramWebhook._ask_for_location(
                user_id=user.user_id,
                keyboard=loc_and_phone_keyboard
            )
        BOT.send_message(
            user_id,
            text=message_text,
            reply_markup=types.ReplyKeyboardRemove(),
        )

    @classmethod
    def _proccess_undefined_message(cls, user_id: int, message: str):
        """
        Обрабатывает неопределенное сообщение.
        """
        try:
            user = TelegramWebhook._get_object_or_none(
                TelegramUser,
                user_id=user_id
            )
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
            # Сценарий если отзыв существует и от юзера ждать нечего
            if review_exists:
                return TelegramWebhook._handle_review_exists_scenario(
                    user_id=user_id
                )
            if not user.task_received:
                return TelegramWebhook.handler_task_not_received(
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
                TelegramWebhook._handle_finall_msg(user_id=user_id)
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
