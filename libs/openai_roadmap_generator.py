import openai
import os
import json
from django.core.exceptions import ObjectDoesNotExist
from .openai_roadmap_generator_schema import SCHEMA
import jsonschema

class AIRoadmapGenerator:
    def __init__(self, attempt_id):
        """
        Initialize the Roadmap Generator with the attempt ID and schema.
        """
        self.schema = SCHEMA
        self.attempt_id = attempt_id
        self.attempt = None
        self.user_name = None
        self.quiz_title = None
        self.quiz_description = None
        self.user_responses = None
        self.response_content = None
        self.products = []

        self.client = openai.Client(
            api_key=os.environ["api_key"],
            organization=os.environ["organization"]
        )

        self._fetch_attempt()

    def _fetch_attempt(self):
        """
        Fetch attempt data and set the user details, quiz details, and responses.
        """
        from apps.quize.models import Attempt  # Replace 'your_app' with the actual app name

        try:
            self.attempt = Attempt.objects.get(id=self.attempt_id)
            self.user_name = self.attempt.respondent.full_name
            self.quiz_title = self.attempt.quiz.title
            self.quiz_description = self.attempt.quiz.description
            self.user_responses = self.attempt.serialize_responses()
            self._serialize_products()
        except ObjectDoesNotExist:
            raise ValueError(f"Attempt with ID {self.attempt_id} does not exist.")

    def _validate_response(self, response):
        """
        Validate the AI response against the defined schema.

        :param response: The AI-generated response content as a Python object.
        :return: True if valid, raises ValueError if invalid.
        """
        from jsonschema import validate, ValidationError

        try:
            validate(instance=response, schema=self.schema)
            return True
        except ValidationError as e:
            raise ValueError(f"Invalid AI response: {e.message}")

    def _handle_incomplete_response(self, response):
        """
        Handle cases where the AI response does not conform to the schema.

        :param response: The partially valid AI response content.
        :return: A fallback response or default values.
        """
        fallback_response = {
            "title": "Roadmap Unavailable",
            "description": "We encountered an issue generating your roadmap. Please try again later.",
            "longevity_score": {},
            "morning_routine": {},
            "midday_strategy": {},
            "evening_habits": {},
            "specific_lifestyle_tips": {},
            "insights": [],
            "product_recommendation": [],
            "encouragement": "Stay motivated! Your roadmap will be ready soon."
        }

        # Log details for debugging in production
        print("Invalid or incomplete AI response detected. Returning fallback.")
        return {**fallback_response, **response}
    

    def _serialize_products(self):
        """
        Fetch and serialize products into a compact format for the AI prompt.

        :return: A JSON-like string containing product keys, titles, and summaries.
        """
        from apps.quize.models import Product
        products = Product.objects.all()
        serialized_products = [
            {
                "product_key": product.key,
                "title": product.title,
                "summary": (product.description[:100] + "...") if product.description else "No description available"
            }
            for product in products
        ]
        self.products = json.dumps(serialized_products, indent=2)


    def _generate_prompt(self):
        """
        Generate the AI prompt based on the quiz data and serialized product information.
        
        :param serialized_products: A list of products with minimal details to include in the prompt.
        :return: The formatted prompt string.
        """

        prompt = f"""
        The user "{self.user_name}" has completed a quiz titled "{self.quiz_title} - {self.quiz_description}". Below are the questions asked and the answers provided:

        {self.user_responses}

        Based on their responses:
        1. Start with a welcoming note thanking the user for completing the quiz and motivating them to take action on their results.
        2. Analyze the user responses and derive a Longevity Score object containing:
            - Score details (value and max_value)
            - Status (Critical, Low, Balanced, Good, Perfect)
            - Description with motivational words based on the status.
        3. Provide actionable sections tailored to their quiz results:
            a. Morning Routine:
                - Include a title and 4-6 steps to energize their day naturally through hydration, nutritious breakfast, and light movement.
            b. Midday Strategy:
                - Include a title and 4-6 steps for combating energy dips, improving digestion, and maintaining focus.
            c. Evening Habits:
                - Include a title and 4-6 steps for relaxation, light dinner suggestions, and preparing for restorative sleep.
            d. Specific Lifestyle Tips:
                - Include a title and 4-6 steps for personalized lifestyle changes such as mindful eating, regular activity, and stress management.
        4. Provide general insights or tips based on the user's quiz results in a list format.
        5. From the following products, recommend up to 2 products that are most suitable based on the user's quiz results. Use the product_key to identify products:
        {self.products}
            - For each recommended product:
                a. Personalize the benefits for the user.
                b. Provide clear and personalized usage instructions.
                Note: Return an empty array if no product list is given.
        6. Conclude with a motivational message to inspire the user on their journey.
        """
        return prompt



    def generate_ai_response(self):
        """
        Generate the roadmap using OpenAI and validate the response.

        :return: Validated AI response content or fallback content.
        """
        if not self.user_responses:
            raise ValueError("User responses must be set before generating the roadmap.")

        prompt = self._generate_prompt()

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in personalized health and wellness roadmaps."},
                    {"role": "user", "content": prompt},
                ],
                functions=[
                    {
                        "name": "generate_personalized_roadmap",
                        "description": "Generates a structured roadmap for user health and wellness",
                        "parameters": self.schema,
                    }
                ],
                function_call={"name": "generate_personalized_roadmap"},
            )

            response_content = json.loads(response.choices[0].message.function_call.arguments)
            self._validate_response(response_content)
            self.response_content = response_content
            return self.response_content

        except ValueError as ve:
            print(f"Validation Error: {ve}")
            return self._handle_incomplete_response({})  # Pass fallback response in case of validation errors

        except Exception as e:
            print(f"Unexpected Error: {e}")
            return self._handle_incomplete_response({})  # Pass fallback response for unexpected errors

    def get_response_content(self):
        """
        Get the validated AI response content.

        :return: AI-generated roadmap content or None if not available.
        """
        if not self.response_content:
            raise ValueError("AI response has not been generated yet.")



        return self.response_content


    # def generate_ai_response_streaming(self):
    #     """
    #     Generate the roadmap using OpenAI with streaming.
    #     :yield: Partial AI response content for real-time streaming.
    #     """
    #     if not self.user_responses:
    #         raise ValueError("User responses must be set before generating the roadmap.")

    #     # existing_report = getattr(self.attempt, 'ai_report', None)
    #     # if existing_report:
    #     #     return existing_report.roadmap

    #     prompt = self._generate_prompt()

    #     try:
    #         # Initialize the streaming request
            
    #         response_stream = self.client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             messages=[
    #                 {"role": "system", "content": "You are an expert in personalized health and wellness roadmaps."},
    #                 {"role": "user", "content": prompt},
    #             ],
    #             functions=[
    #                 {
    #                     "name": "generate_personalized_roadmap",
    #                     "description": "Generates a structured roadmap for user health and wellness",
    #                     "parameters": self.schema,
    #                 }
    #             ],
    #             function_call={"name": "generate_personalized_roadmap"},
    #             stream=True
    #         )

    #         # Stream and yield content as received
    #         for chunk in response_stream:
    #             for choice in chunk.choices:
    #                 delta = choice.delta
    #                 if delta.function_call:
    #                     content = delta.function_call.arguments
    #                     if content:
    #                         yield content

    #     except Exception as e:
    #         # Handle errors gracefully by yielding an error message
    #         error_message = f"An error occurred: {e}"
    #         print(error_message)  # Log the error for debugging
    #         yield error_message


    def save_ai_report(self, complete_response):
        from apps.quize.models import AIReport
        """
        Save the complete AI response to the database.
        :param complete_response: The complete AI response as a string.
        """
        try:
            # Parse the response into JSON (if required)
            response_json = json.loads(complete_response)

            # Save the response to the AIReport model
            ai_report, created = AIReport.objects.update_or_create(
                attempt=self.attempt,
                defaults={
                    "roadmap": response_json,
                    "total_tokens": len(complete_response),  # Or use actual token count if available
                },
            )
            print(f"AI report saved successfully. Created: {created}")
        except Exception as e:
            print(f"Failed to save AI report: {e}")


    def generate_ai_response_streaming(self):
        """
        Generate the roadmap using OpenAI with streaming and save it to the database.
        :yield: Partial AI response content for real-time streaming.
        """
        if not self.user_responses:
            raise ValueError("User responses must be set before generating the roadmap.")

        existing_report = getattr(self.attempt, "ai_report", None)
        if existing_report:
            ai_roadmap = json.dumps(existing_report.roadmap)
            chunk_size = 4            
            # Stream the existing roadmap from the database as JSON
            for i in range(0, len(ai_roadmap), chunk_size):
                content = ai_roadmap[i:i + chunk_size]
                yield content  # Yield each top-level key-value pair as a JSON object
            
            return  # Stop further execution if the report exists

        prompt = self._generate_prompt()

        # Initialize a variable to accumulate the complete response
        complete_response = ""

        try:
            # Initialize the streaming request
            response_stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in personalized health and wellness roadmaps."},
                    {"role": "user", "content": prompt},
                ],
                functions=[
                    {
                        "name": "generate_personalized_roadmap",
                        "description": "Generates a structured roadmap for user health and wellness",
                        "parameters": self.schema,
                    }
                ],
                function_call={"name": "generate_personalized_roadmap"},
                stream=True
            )

            # Stream and yield content as received
            for chunk in response_stream:
                for choice in chunk.choices:
                    delta = choice.delta
                    if delta.function_call:
                        content = delta.function_call.arguments
                        if content:
                            # Append the chunk to the complete response
                            complete_response += content
                            # Yield the chunk for real-time streaming
                            yield content

            # Save the complete response to the database once streaming is finished
            if complete_response:
                self.save_ai_report(complete_response)

        except Exception as e:
            # Handle errors gracefully by yielding an error message
            error_message = f"An error occurred: {e}"
            print(error_message)  # Log the error for debugging
            yield error_message
