from django.db import models
import uuid

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from libs.openai_roadmap_generator import *
from django.db import transaction

User = get_user_model()



# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver



class Product(models.Model):
    key = models.CharField(max_length = 50, unique = True)
    title = models.CharField(max_length=255)
    link = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to = "product-thumbnail")



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

    def serialize_responses(self):
        responses = []
        for user_response in self.responses.all():
            user_response_dict = user_response.get_response()
            responses.append(user_response_dict)
        return responses
    
    def generate_report(self):
        # Check if the AI report already exists
        existing_report = getattr(self, 'ai_report', None)
        if existing_report:
            return existing_report.roadmap

        try:
            ai_roadmap_gen = AIRoadmapGenerator(attempt_id=self.id)
            ai_response = ai_roadmap_gen.generate_ai_response()
            ai_output = ai_roadmap_gen.get_response_content()

            # Save the generated report atomically
            with transaction.atomic():
                report = AIReport.objects.create(
                    attempt=self,
                    roadmap=ai_output,
                    total_tokens=5000
                )
                return report.roadmap

        except Exception as e:
            print(f"Error generating AI report for Attempt ID {self.id}: {e}")
            raise


    def get_ai_report(self):
        ai_report = self.generate_report()
        ai_report_with_products = AIReport.populate_product_data(ai_report)
        return ai_report_with_products

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

    def get_response(self):
        question = self.question
        answer = ""

        if question.question_type in ["text", "number"]:
            answer = self.answer
        else:
            for sso in self.selected_option.all():
                answer += f"{sso.text}, "

        return {
            'question': question.question_text,
            'answer': answer
        }
    # def clean(self):
    #     from django.core.exceptions import ValidationError

    #     if not self.answer and not self.selected_option.exists():
    #         raise ValidationError("Either 'answer' or 'selected_option' must be provided.")


    def __str__(self):
        return f"Response for {self.question} in {self.attempt}"



class AIReport(models.Model):
    attempt = models.OneToOneField(
        "Attempt", on_delete=models.CASCADE, related_name="ai_report", db_index=True
    )
    roadmap = models.JSONField(null=True, default=dict)
    total_tokens = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def populate_product_data(ai_roadmap):
        try:
            # Ensure 'product_recommendation' exists in the roadmap
            if not isinstance(ai_roadmap, dict):
                raise ValueError("The AI roadmap must be a dictionary.")

            ai_roadmap.setdefault("product_recommendation", [])

            # Populate the product_recommendation section with actual product data
            for product in ai_roadmap["product_recommendation"]:
                product_key = product.get('product_key')
                if product_key:
                    # Fetch the product using the product_key
                    product_object = Product.objects.filter(key=product_key).first()
                    if product_object:
                        product["product_object"] = {
                            "title": product_object.title,
                            "thumbnail": product_object.thumbnail.url if product_object.thumbnail else None,
                            "link": str(product_object.link) if product_object.link else None,
                        }

            return ai_roadmap

        except Exception as e:
            raise ValueError(f"An error occurred while updating the product data: {e}")

  
    def __str__(self):
        return f"AI Report for Attempt ID: {self.attempt_id}"