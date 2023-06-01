from loguru import logger
from telebot import types
from datetime import timedelta
from django.utils import timezone

from celery import shared_task

from .models import Commands


@shared_task
def test():
    Commands.objects.create(
        cmd="TEST",
        text="check"
    )
    logger.info("CHECK")
