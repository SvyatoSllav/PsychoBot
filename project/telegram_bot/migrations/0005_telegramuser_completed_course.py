# Generated by Django 4.1.4 on 2023-06-02 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0004_alter_telegramuser_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='completed_course',
            field=models.BooleanField(default=False, verbose_name='Завершил курс'),
        ),
    ]