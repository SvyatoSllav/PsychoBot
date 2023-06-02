# Generated by Django 4.1.4 on 2023-06-02 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psycho_survey', '0011_questionnaire_unique_is_active'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='questionnaire',
            name='unique_is_active',
        ),
        migrations.AddConstraint(
            model_name='questionnaire',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('is_active',), name='unique_is_active', violation_error_message='SMT'),
        ),
    ]