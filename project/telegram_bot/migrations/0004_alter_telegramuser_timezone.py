# Generated by Django 4.1.4 on 2023-06-01 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0003_alter_telegramuser_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='timezone',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
