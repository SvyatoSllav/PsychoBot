import pytz
import time
from datetime import datetime

from celery import shared_task

from loguru import logger

from psycho_survey.models import Task, Questionnaire

from .models import TelegramUser
from .loader import BOT
from .utils import send_to_user_active_task


@shared_task
def send_daily_msg():
    try:
        started_course_users = TelegramUser.objects.filter(
            bought_course=True,
            completed_course=False,
        ).exclude(
            timezone='',
        )
        for user in started_course_users:
            time_to_sent_msg = check_time_in_timezone(
                user.timezone,
                hour=10,
                minute=00
            )
            time_to_reset_task = check_time_in_timezone(
                user.timezone,
                hour=00,
                minute=00
            )
            if time_to_sent_msg:
                send_to_user_active_task(
                    user_id=user.user_id,
                    day_number=user.day_number
                )
            if time_to_reset_task:
                if user.task_sent:
                    user.task_sent = False
                    user.day_number = user.day_number + 1
                    user.save()
                    return user
                user.day_number = user.day_number - 1
                user.save()
    except Exception as _exec:
        logger.error(f"{_exec}")
        return "Timezone is undefined"


def check_time_in_timezone(timezone: str, hour: int, minute: int):
    # Get the current time in the specified timezone
    target_timezone = pytz.timezone(timezone)
    target_time = datetime.now(target_timezone)

    # Remove the UTC offset from the time string
    local_time = target_time.astimezone()

    # Extract the hour and minute from the time string
    local_hour = local_time.hour
    local_minute = local_time.minute
    logger.info(f"{local_hour}, {local_minute}")

    return local_hour == hour and local_minute == minute
