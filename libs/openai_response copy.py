import json
import openai
import os

client = openai.Client(
    api_key=os.environ["api_key"], organization=os.environ["organization"]
)

ASSISTANT_ID = os.environ["ASSISTANT_ID"]


class AnalysisResponse:
    def __init__(self, survey_title, survey_category, response):
        self.survey_title = survey_title
        self.survey_category = survey_category
        self.response = response
        self.prompt = None
        self.response_content = None
        self.assistant_id = ASSISTANT_ID

    def generate_prompt(self):
        # Dynamically generate the prompt based on questions and answers
        responses_text = "\n".join(
            f"{i+1}. Q: {qa['question']}\n   A: {qa['answer']}"
            for i, qa in enumerate(self.response)
        )

        self.prompt = (
            f"Survey Title: {self.survey_title}\n"
            f"Survey Category: {self.survey_category}\n\n"
            f"Survey Responses:\n{responses_text}\n\n"
            f"Task:\n"
            f"Based on the responses, provide the following in JSON format:\n"
            "{\n"
            '    "analysis": {self.survey_category} : "Evaluate the responses and provide insights about the {self.survey_category} habits.}",\n'
            '    "summary": "Briefly summarize the overall {self.survey_category} habits of the respondent. in array list",\n'
            '    "score": " totle_score: Assign a {self.survey_category} score out of 10 based on the responses.",\n'
            '    "strength": "Highlight one strong aspect of their {self.survey_category} habits. in array list",\n'
            '    "weakness": "Identify one area of improvement in their {self.survey_category} habits. in array list",\n'
            '    "long_term_goal": "Suggest a long-term {self.survey_category} goal for the respondent. in array list",\n'
            '    "short_term_goal": "Suggest a short-term actionable {self.survey_category} goal. in array list",\n'
            '    "conclusion": "content: Conclude with motivational advice or encouragement for the respondent."\n'
            "}"
        )

        return self.prompt

    def call_openapi(self):
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # gpt-4 | gpt-4o-mini
            # assistant_id=self.assistant_id,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a {self.survey_category} assistant with ID '{self.assistant_id} analyzing survey data.",
                },
                {"role": "user", "content": self.prompt},
            ],
        )

        # assistant = client.beta.assistants.create(            
        #     name="Math Tutor",
        #     instructions="You are a personal math tutor. Write and run code to answer math questions.",
        #     model="gpt-4o",
        # )
        # print(assistant)
        self.response_content = response.choices[0].message.content
        return self.response_content

    def get_results(self):
        cleaned_response = (
            self.response_content.strip()
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        # print(cleaned_response)
        result_dict = json.loads(cleaned_response)

        return result_dict


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
    x.call_openapi()
    _ = x.get_results()
    print(_)
