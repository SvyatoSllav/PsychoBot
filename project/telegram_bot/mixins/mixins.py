import time

from timezonefinder import TimezoneFinder

from telebot import types

from telegram_bot.models import TelegramUser, Commands
from telegram_bot.loader import BOT
from telegram_bot.consts import messages_const
from telegram_bot.keyboards import get_loc_and_phone_keyboard

from psycho_survey.models import Messages, Review, Task


class ReviewValidators:
    pass


class TaskValidators:
    @classmethod
    def _is_waiting_for_msgs(cls, task: Task, task_msg_count: int):
        """
        Проверяет, ожидаем ли еще сообщений по задачу.
        """
        task_special = task.is_answer_counted_task
        not_enough_msg = task.amount_of_message != task_msg_count
        return not_enough_msg and task_special

    @classmethod
    def _is_task_finall_msg(cls, task: Task, task_msg_count: int):
        """
        Проверяем, является ли сообщение по задаче последним.
        """
        task_special = task.is_answer_counted_task
        enough_msg = task.amount_of_message == task_msg_count
        return enough_msg and task_special


class MessagesValidators:
    @classmethod
    def _get_latest_message_or_zero(cls, user: TelegramUser) -> int:
        """
        Получаем счетчик последнего сообщения или ноль.
        """
        obj = Messages.objects.filter(user=user)
        if obj.exists():
            last_msg = Messages.objects.filter(user=user).latest("created_at")
            return last_msg.msg_count
        return 0


class ValidatorsMixin(ReviewValidators, TaskValidators, MessagesValidators):
    @classmethod
    def _get_object_or_none(cls, model, **kwargs):
        """
        Получает объект переданной модели по переданным ключам.
        """
        obj = model.objects.filter(**kwargs)
        if obj.exists():
            return obj[0]


class MessageHandlers:
    @classmethod
    def _handle_review_exists_scenario(cls, user_id: int):
        """
        Сценарий при сообщении, когда отзыв уже создан.
        Если отзыв создан, неявно предполагается, что курс пройден.
        """
        BOT.send_chat_action(chat_id=user_id, action="typing")
        time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text=messages_const.REVIEW_IS_EXISTS,
        )

    @classmethod
    def _ask_for_location(cls, user_id: int, keyboard):
        """
        Запрашивает локацию и телефон у пользователя.
        """
        BOT.send_chat_action(chat_id=user_id, action="typing")
        time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text=messages_const.SEND_YOUR_LOCATION_OR_PHONE,
            reply_markup=keyboard
        )

    @classmethod
    def _task_completed_scenario(cls, user: TelegramUser, message: str):
        """
        Сценарий если задача выполнена.
        """
        BOT.send_chat_action(chat_id=user.user_id, action="typing")
        time.sleep(5)
        if user.day_number == 10:
            Review.objects.create(
                user=user,
                text=message,
            )
            BOT.send_message(
                chat_id=user.user_id,
                text=messages_const.GRATITUDE_FOR_REVIEW
            )
            return
        BOT.send_message(
            chat_id=user.user_id,
            text=messages_const.TASK_ALREADY_SENT
        )

    @classmethod
    def _wait_for_msgs(
            cls,
            user: TelegramUser,
            task: Task,
            message: str,
            task_msg_count: int):
        """
        Функция подсчета и сохранения сообщений при ожидании
        больше 1 сообщения в задаче.
        """
        incremented_msg_count = task_msg_count + 1
        Messages.objects.create(
            user=user,
            task=task,
            message_text=message,
            msg_count=incremented_msg_count,
        )

    @classmethod
    def _save_finall_msg(cls, user_id: int):
        """
        Сохраняет последнее сообщение при ожидании больше 1 сообщения в задаче
        """
        BOT.send_chat_action(chat_id=user_id, action="typing")
        time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text=messages_const.MESSAGES_SAVED,
        )

    @classmethod
    def _save_review(cls, user: TelegramUser, message: int):
        """
        Сохраняет отзыв.
        """
        BOT.send_chat_action(chat_id=user.user_id, action="typing")
        time.sleep(5)
        Review.objects.create(
            user=user,
            text=message
        )
        BOT.send_message(
            chat_id=user.user_id,
            text=messages_const.SENT_REVIEW
        )

    @classmethod
    def _handle_task_message(
            cls,
            user: TelegramUser,
            task: Task,
            message: str):
        """
        Сохраняет сообщение при обычном типе задач.
        """
        Messages.objects.create(
            user=user,
            task=task,
            message_text=message,
        )
        user.task_sent = True
        user.save()
        BOT.send_chat_action(chat_id=user.user_id, action="typing")
        time.sleep(5)
        BOT.send_message(
            chat_id=user.user_id,
            text=messages_const.GRATITUDE_FOR_TASK_ANSWER
        )

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

    @classmethod
    def _process_help_cmd(cls, user_id):
        """
        Обрабатывает команду /help
        """
        start_cmd_text = Commands.objects.get(cmd="/help")
        if start_cmd_text:
            BOT.send_message(user_id, start_cmd_text.text)
            return
        BOT.send_message(user_id, "Хелповое сообщение")
