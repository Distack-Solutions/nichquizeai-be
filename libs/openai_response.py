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
        "title": {"type": "string", "description": "The title of the roadmap"},
        "roadmap_description": {"type": "string", "description": "Description of the roadmap starting with thanking user to take this quiz"},
        "performance_analytics": {
            "type": "array",
            "description": "Performance metrics based on quiz results",
            "items": {
                "type": "object",
                "properties": {
                    "param_name": {
                        "type": "string",
                        "description": "The name of the performance parameter, e.g., 'Sleep Quality' or 'Stress Level'"
                    },
                    "param_description": {
                        "type": "string",
                        "description": "Detailed description of the parameter"
                    },
                    "score": {
                        "type": "object",
                        "description": "Scoring details",
                        "properties": {
                            "value": {
                                "type": "number",
                                "description": "The score for this parameter"
                            },
                            "max_value": {
                                "type": "number",
                                "description": "The maximum possible score for this parameter"
                            }
                        },
                        "required": ["value", "max_value"]
                    }
                },
                "required": ["param_name", "param_description", "score"]
            }
        },
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the section"},
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Name of the step"},
                                "description": {"type": "string", "description": "Details about the step"}
                            },
                            "required": ["title", "description"]
                        }
                    }
                },
                "required": ["title", "steps"]
            }
        },
        "insights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "insight": {"type": "string", "description": "General insight or tip based on quiz results"}
                },
                "required": ["insight"]
            }
        },
        "product_recommendation": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Name of the product"},
                    "benefits": {"type": "array", "items": {"type": "string", "description": "Product benefits"}},
                    "usage_instructions": {"type": "string", "description": "How to use the product"}
                },
                "required": ["product_name", "benefits", "usage_instructions"]
            }
        },
        "encouragement": {
            "type": "string",
            "description": "Motivational message to inspire the user on their journey"
        }
    },
    "required": [
        "title", 
        "roadmap_description",
        "performance_analytics",
        "sections",
        "insights",
        "product_recommendation",
        "encouragement"
    ]
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
        prompt = ""
        

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
