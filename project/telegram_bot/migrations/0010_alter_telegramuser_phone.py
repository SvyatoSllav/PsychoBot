# Generated by Django 4.1.4 on 2023-06-03 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0009_telegramuser_order_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=17, verbose_name='Номер телефона'),
        ),
    ]
