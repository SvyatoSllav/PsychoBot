# Generated by Django 4.1.4 on 2023-05-30 22:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0002_alter_commands_options_and_more'),
        ('psycho_survey', '0006_alter_questionnaire_eighth_task_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('message_text', models.TextField(max_length=4000, verbose_name='Текст сообщения')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psycho_survey.task', verbose_name='Задача')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_bot.telegramuser', verbose_name='Сообщение')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
