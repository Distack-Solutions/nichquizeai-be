from django.contrib import admin
from .models import *


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_by", "created_at", "updated_at")
    search_fields = ("title", "category", "created_by__username")
    list_filter = ("category", "created_at")
    ordering = ("-created_at",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "question_type", "quiz")
    search_fields = ("question_text", "quiz__title")
    list_filter = ("question_type", "quiz")
    ordering = ("quiz",)


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("text", "question")
    search_fields = ("text", "question__question_text")
    ordering = ("question",)


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email")
    search_fields = ("full_name", "email")
    ordering = ("full_name",)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "respondent")
    search_fields = ("quiz__title", "respondent__full_name")
    ordering = ("quiz",)


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'attempt', 'display_selected_options', 'answer')
    search_fields = ('question__question_text', 'attempt__respondent__full_name', 'answer')
    ordering = ('-id',)

    def display_selected_options(self, obj):
        return ", ".join([option.text for option in obj.selected_option.all()])

    display_selected_options.short_description = "Selected Options"


@admin.register(AIReport)
class AIReportAdmin(admin.ModelAdmin):
    list_display = ("attempt",)
