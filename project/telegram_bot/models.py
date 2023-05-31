from django.db import models
from .mixins import UUIDMixin, TimeStampedMixin
from django.core.validators import MaxValueValidator, MinValueValidator


class TelegramUser(UUIDMixin, TimeStampedMixin):
    user_id = models.BigIntegerField(verbose_name='Юзер ID', unique=True)
    username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Юзернейм'
    )
    day_number = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        verbose_name='Номер дня'
    )
    bought_course = models.BooleanField(
        default=False,
        verbose_name="Купил курс"
    )
    task_sent = models.BooleanField(
        default=False,
        verbose_name="Сдал задачу"
    )
    timezone = models.DateTimeField(
        auto_now_add=False,
        verbose_name="timezone",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"""
        {self.user_id}
        {self.username}
        """

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Commands(UUIDMixin, TimeStampedMixin):
    cmd = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Название команды'
    )
    text = models.TextField(
        max_length=4000,
        blank=False,
        verbose_name='Текст сообщения'
    )

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'
