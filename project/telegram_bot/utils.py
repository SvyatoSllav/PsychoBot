from enum import Enum
import time

from typing import Optional

from psycho_survey.models import Questionnaire, Task

from .loader import BOT


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
        return Task.objects.get(day_number=day_number).text_of_task


def send_to_user_active_task(user_id: int, day_number: int):
    """
    Получает у юзера активную задачу и отправляет её.
    """
    full_text = get_active_task(day_number=day_number)
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


class PaymentStatus(Enum):

    NONE = "NONE"
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    REFUNDED = "REFUNDED"

    @classmethod
    def choices(cls):
        # print(tuple((i.name, i.value) for i in cls))
        return tuple((i.name, i.value) for i in cls)


def check_payment_status():
    pass
