# Generated by Django 4.1.4 on 2023-05-31 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psycho_survey', '0008_alter_messages_options_alter_messages_user_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='msg_count',
            field=models.IntegerField(default=0),
        ),
    ]
