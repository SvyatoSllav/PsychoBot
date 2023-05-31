from django.contrib import admin
from .models import Task, Questionnaire, Messages


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "day_number",
        "text_of_task",
        "is_answer_counted_task",
    ]


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = [
        "first_task",
        "is_active",
    ]


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "task",
        "message_text",
    ]
    search_fields = [
        "user",
        "task",
    ]
