from django.db import models
import uuid

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver

class Quiz(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, null=True, blank=True, default="Productivity Quiz")
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-updated_at',)

    def __str__(self):
        return self.title


class Question(models.Model):
    TEXT = "text"
    NUMBER = "number"
    CHECKBOXES = "checkboxes"
    RADIO = "radio"

    QUESTION_TYPES = [
        (TEXT, "Text"),
        (NUMBER, "Number"),
        (CHECKBOXES, "Checkboxes"),
        (RADIO, "Radio"),
    ]

    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default=TEXT
    )
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="questions")

    def __str__(self):
        return self.question_text


class QuestionOption(models.Model):
    text = models.CharField(max_length=255)
    image = models.ImageField(upload_to="question_options/", blank=True, null=True)
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, related_name="options"
    )

    def __str__(self):
        return self.text


class Respondent(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.full_name


class Attempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE, related_name="attempts")
    respondent = models.ForeignKey(
        "Respondent", on_delete=models.CASCADE, related_name="attempts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Attempt by {self.respondent} on {self.quiz}"


class Response(models.Model):
    answer = models.TextField(blank=True, null=True)
    selected_option = models.ManyToManyField("QuestionOption", blank=True)
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, related_name="responses"
    )
    attempt = models.ForeignKey(
        "Attempt", on_delete=models.CASCADE, related_name="responses"
    )

    # def clean(self):
    #     from django.core.exceptions import ValidationError

    #     if not self.answer and not self.selected_option.exists():
    #         raise ValidationError("Either 'answer' or 'selected_option' must be provided.")


    def __str__(self):
        return f"Response for {self.question} in {self.attempt}"


class AIReport(models.Model):
    attempt = models.ForeignKey(
        "Attempt", on_delete=models.CASCADE, related_name="report_attempt"
    )
    analysis_report = models.JSONField(null=True)
    # summary = models.JSONField(null=True)
    # score = models.JSONField(null=True)
    # strength = models.JSONField(null=True)
    # weakness = models.JSONField(null=True)
    # long_term_goal = models.JSONField(null=True)
    # short_term_goal = models.JSONField(null=True)
    # conclusion = models.JSONField(null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
