from django.contrib import admin
from .models import Task, Questionnaire, Messages, Review


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "day_number",
        "text_of_task",
        "is_answer_counted_task",
    ]

    search_fields = ["name", "text_of_task"]
    list_filter = ["name", "day_number", "is_answer_counted_task", ]


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = [
        "first_task",
        "is_active",
    ]

    search_fields = ["first_task", ]
    list_filter = ["is_active", ]


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "task",
        "message_text",
    ]
    exclude = ['msg_count', ]
    search_fields = [
        "user",
        "task",
    ]
    list_filter = ["user", "task"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "text",
    ]
    search_fields = [
        "user",
        "text"
    ]
    list_filter = ["user", "text"]
