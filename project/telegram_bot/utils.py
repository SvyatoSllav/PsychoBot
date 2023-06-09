from enum import Enum
import time

from typing import Optional

from django.http import JsonResponse
from loguru import logger

from core import settings
from psycho_survey.models import Questionnaire, Task
from .Tinkoff import TinkoffSimplePayment

from .loader import BOT
from .models import TelegramUser


def get_active_task(day_number: int) -> Optional[Task]:
    """
    Получает активную задачу.
    """
    quiz = Questionnaire.objects.filter(is_active=True)
    if quiz.exists():
        day_to_task = {
            1: quiz[0].first_task,
            2: quiz[0].second_task,
            3: quiz[0].third_task,
            4: quiz[0].fourth_task,
            5: quiz[0].fifth_task,
            6: quiz[0].sixth_task,
            7: quiz[0].seventh_task,
            8: quiz[0].eighth_task,
            9: quiz[0].nineth_task,
            10: quiz[0].tenth_task,
        }
        return day_to_task[day_number]
    elif Task.objects.filter(day_number=day_number).exists():
        return Task.objects.get(day_number=day_number)


def send_to_user_active_task(user_id: int, day_number: int):
    """
    Получает у юзера активную задачу и отправляет её.
    """
    user = TelegramUser.objects.get(user_id=user_id)
    user.task_received = True
    user.save()
    full_text = get_active_task(day_number=day_number).text_of_task
    text_chunk_size = 1000
    # Разбивает сообщение на равные части по 1000 символов
    messages = [full_text[i:i+text_chunk_size] for i in range(0, len(full_text), text_chunk_size)]
    for message in messages:
        BOT.send_chat_action(chat_id=user_id, action="typing")
        time.sleep(5)
        BOT.send_message(
            chat_id=user_id,
            text=message or "Пока нет активных заданий",
        )


def get_payment_url(user: TelegramUser) -> str:
    """
    Генерирует и возвращает ссылку на форму оплаты.
    """
    try:
        payment = TinkoffSimplePayment(
            terminal_id=settings.TERMINAL_KEY,
            password=settings.PASSWORD
        )
        order_id = str(user.id)
        payment_result = payment.init(
            order_id, settings.AMOUNT,
            sign_request=True,
            notificationURL=settings.NOTIFICATION_URL,
            data={"Phone": user.phone}
        )
        payment_url = payment_result['PaymentURL']
        return payment_url

    except AttributeError as _exec:
        logger.error(_exec)
        return JsonResponse({"Error": "User not found"})
    except Exception as _exec:
        logger.error(f"{_exec}")
        return JsonResponse({"Error": "error during payment"})


def check_payment_status():
    pass
