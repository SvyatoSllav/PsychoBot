# Generated by Django 4.1.4 on 2023-05-30 20:56

import django.core.validators
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commands',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('cmd', models.CharField(max_length=100, verbose_name='Название команды')),
                ('text', models.TextField(max_length=4000, verbose_name='Текст сообщения')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('user_id', models.BigIntegerField(unique=True, verbose_name='Юзер ID')),
                ('username', models.CharField(blank=True, max_length=100, verbose_name='Юзернейм')),
                ('day_number', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)], verbose_name='Номер дня')),
                ('bought_course', models.BooleanField(default=False)),
                ('task_sent', models.BooleanField(default=False, verbose_name='Сдал задачу')),
                ('timezone', models.DateTimeField(blank=True, null=True, verbose_name='timezone')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
    ]
