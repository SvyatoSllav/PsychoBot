# Generated by Django 4.1.4 on 2023-05-30 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commands',
            options={'verbose_name': 'Команда', 'verbose_name_plural': 'Команды'},
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='bought_course',
            field=models.BooleanField(default=False, verbose_name='Купил курс'),
        ),
    ]
