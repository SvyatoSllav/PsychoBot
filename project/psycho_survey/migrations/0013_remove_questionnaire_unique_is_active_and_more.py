# Generated by Django 4.1.4 on 2023-06-02 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psycho_survey', '0012_remove_questionnaire_unique_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='questionnaire',
            name='unique_is_active',
        ),
        migrations.AddConstraint(
            model_name='questionnaire',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('is_active',), name='unique_is_active', violation_error_message='Уже существует активный тест.'),
        ),
    ]
