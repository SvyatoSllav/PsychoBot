from django.db import models
from django.core.exceptions import ValidationError

from django.core.validators import MaxValueValidator, MinValueValidator

from telegram_bot.mixins.models_mixins import UUIDMixin, TimeStampedMixin
from telegram_bot.models import TelegramUser


class Task(UUIDMixin, TimeStampedMixin):
    name = models.CharField(
        max_length=150,
        verbose_name="Название задачи")
    day_number = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        verbose_name='Номер дня'
    )
    text_of_task = models.TextField(
        max_length=4000,
        blank=False,
        verbose_name='Текст сообщения'
    )
    is_answer_counted_task = models.BooleanField(
        default=False,
        verbose_name="Особая задача"
    )
    amount_of_message = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1, message="Минимальное значение равно 1."),
        ],
    )

    def clean(self):
        """
        Проверяет, что количество ожидаемый сообщений заполнено
        если задача выбрана "особой"
        """
        if self.is_answer_counted_task and self.amount_of_message:
            if self.amount_of_message < 1:
                raise ValidationError("Выберите количество сообщений")

    def __str__(self):
        return f"{self.name} День: {self.day_number}"

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class Questionnaire(UUIDMixin, TimeStampedMixin):
    first_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Первая задача",
        related_name="quest_first_task",
    )
    second_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Вторая задача",
        related_name="quest_second_task",
    )
    third_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Третья задача",
        related_name="quest_third_task",
    )
    fourth_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Четвертая задача",
        related_name="quest_fourth_task",
    )
    fifth_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Пятая задача",
        related_name="quest_fifth_task",
    )
    sixth_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Шестая задача",
        related_name="quest_sixth_task",
    )
    seventh_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Седьмая задача",
        related_name="quest_seventh_task",
    )
    eighth_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Восьмая задача",
        related_name="quest_eighth_task",
    )
    nineth_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Девятая задача",
        related_name="quest_nineth_task",
    )
    tenth_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Десятая задача",
        related_name="quest_tenth_task",
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Активный тест"
    )

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                name='unique_is_active',
                condition=models.Q(is_active=True),
                violation_error_message="Уже существует активный тест."
            )
        ]


class Messages(UUIDMixin, TimeStampedMixin):
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Автор",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Задача",
    )
    message_text = models.TextField(
        max_length=4000,
        blank=False,
        verbose_name='Текст сообщения'
    )
    msg_count = models.IntegerField(
        default=0,
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Review(UUIDMixin, TimeStampedMixin):
    user = models.OneToOneField(
        TelegramUser,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Автор отзыва",
    )
    text = models.TextField(
        max_length=4000,
        blank=False,
        verbose_name='Текст отзыва'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
