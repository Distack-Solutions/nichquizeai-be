import json
import openai
import os

from apps.quize.models import Attempt, Response

client = openai.Client(
    api_key=os.environ["api_key"], organization=os.environ["organization"]
)

ASSISTANT_ID = os.environ["ASSISTANT_ID"]


SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "the title of road map"},
        "description": {"type": "string", "description": "the description of road map"},
        "longevity_score": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "number",
                    "description": "Overall health score based on quiz results",
                },
                "category": {
                    "type": "string",
                    "description": "Category of health status, e.g., Balanced, Needs Improvement",
                },
                "summary": {
                    "type": "string",
                    "description": "High-level summary of the user's health status",
                },
            },
            "required": ["score", "category", "summary"],
        },
        "personalized_roadmap": {
            "type": "object",
            "properties": {
                "morning_routine": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the step in the morning routine",
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the step and how it helps",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
                "midday_strategies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the midday strategy",
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the strategy and its benefits",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
                "evening_habits": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Name of the evening habit",
                            },
                            "description": {
                                "type": "string",
                                "description": "Details about the habit and how it supports health",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
                "specific_lifestyle_tips": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tip": {
                                "type": "string",
                                "description": "Specific lifestyle tip for the user",
                            }
                        },
                        "required": ["tip"],
                    },
                },
            },
            "required": [
                "morning_routine",
                "midday_strategies",
                "evening_habits",
                "specific_lifestyle_tips",
            ],
        },
        "product_recommendation": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Name of the recommended product",
                },
                "benefits": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "List of benefits of the recommended product",
                    },
                },
                "usage_instructions": {
                    "type": "string",
                    "description": "How to use the product effectively",
                },
            },
            "required": ["product_name", "benefits", "usage_instructions"],
        },
        "encouragement": {
            "type": "string",
            "description": "Motivational message to inspire the user on their wellness journey",
        },
    },
    "required": [
        "longevity_score",
        "personalized_roadmap",
        "product_recommendation",
        "encouragement",
    ],
}


class AnalysisResponse:
    def __init__(self, attemptID):
        self.attemptID = attemptID
        self.survey_title = None
        self.survey_description = None
        self.user_response = None
        self.response_content = None

    def init_prompt(self):
        attempt = Attempt.objects.get(id=self.attemptID)
      
        self.survey_title = attempt.quiz.title
        self.survey_description = attempt.quiz.description
        questions_and_answers = []
        items = Response.objects.filter(attempt=attempt)
        for item in items:
            question = item.question
            _qa = {"question": question.question_text, "answer": ""}
            # print(question)
            if question.question_type == "text":
                _qa["answer"] = item.answer
            if (
                question.question_type == "radio"
                or question.question_type == "checkboxes"
            ):
                options_list = list(
                    item.selected_option.all().values_list("text", flat=True)
                )
                _qa["answer"] = ", ".join(options_list)
            
            questions_and_answers.append(_qa)

        self.user_response = questions_and_answers
        # print(self.user_response)
        return self.user_response


    def call_openapi(self):
        # Define your prompt
        prompt = f"""
        You are an expert in health and wellness. Analyze the provided quiz data and generate a personalized roadmap.

        SURVEY TITLE: {self.survey_title}
        SURVEY DESCRIPTION: {self.survey_description}
        USER QUESTION AND ANSWERS.:
        {self.user_response}
        """

        # Make the request
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # gpt-4 | gpt-4o-mini
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in personalized health and wellness roadmaps.",
                },
                {"role": "user", "content": prompt},
            ],
            functions=[
                {
                    "name": "generate_personalized_roadmap",
                    "description": "Generates a structured roadmap for user health and wellness",
                    "parameters": SCHEMA,
                }
            ],
            function_call={
                "name": "generate_personalized_roadmap"
            },  # Ensures the AI outputs structured data
        )

        self.response_content = response.choices[0].message.function_call.arguments
        return self.response_content




if __name__ == "__main__":
    survey_title = "Your Daily Health Habits: A Self-Reflection Survey"
    survey_category = "health"
    questions_and_answers = [
        {
            "question": "How many glasses of water do you drink in a day?",
            "answer": "10",
        },
        {
            "question": "What do you usually eat for breakfast, and how healthy do you think it is?",
            "answer": "I take biryani, and I think I am OK.",
        },
    ]
    x = AnalysisResponse(survey_title, survey_category, questions_and_answers)
    x.generate_prompt()
    # x.call_openapi()
    x.q()
    # _ = x.get_results()
