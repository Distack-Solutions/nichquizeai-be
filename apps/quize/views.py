from django.template.loader import render_to_string
from django.shortcuts import render
from django.shortcuts import render, redirect

# utils
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *

from django.views.generic import ListView
from .models import Quiz  # Replace with your actual model name
from django.views.generic import DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from functools import wraps



def handle_object_not_found(model, param_name, url_name='quize_list', message="The requested object does not exist."):
    """
    A decorator to handle get_object_or_404 exceptions and redirect the user.

    :param model: The model class to query.
    :param param_name: The name of the URL parameter to use for querying.
    :param url_name: The name of the URL to redirect to in case of an error.
    :param message: The error message to display to the user.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj_id = kwargs.get(param_name)  # Fetch the ID from URL parameters
            if not obj_id:
                messages.error(request, f"Invalid URL parameter: {param_name}")
                return redirect(url_name)
            try:
                obj = get_object_or_404(model, id=obj_id)
            except Exception:
                messages.error(request, message)
                return redirect(url_name)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



@method_decorator(login_required, name="dispatch")
class QuizListView(ListView):
    model = Quiz
    template_name = 'quize/list-new.html'  # Update with your template name
    context_object_name = 'quizzes'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        status_filter = self.request.GET.get('status', 'all')

        # Filter by search query if provided
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query))

        # Filter by status if provided
        if status_filter == 'published':
            queryset = queryset.filter(is_published=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_published=False)

        return queryset.order_by('-id')  # Order by latest quizzes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', 'all')
        return context


@login_required
@handle_object_not_found(Quiz, 'quiz_id')
def quiz_detail(request, quiz_id):
    # Get the quiz instance by UUID (or return a 404 if not found)
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Fetch related questions and attempts
    questions = quiz.questions.all()
    responses = quiz.attempts.all()

    # Prepare context data to be passed to the template
    context = {
        'quiz': quiz,
        'questions': questions,
        'responses': responses,
    }

    return render(request, 'quize/quiz-detail.html', context)


@login_required
def create_quiz(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category", "Productivity Quiz")
        
        quiz = Quiz.objects.create(
            title=title,
            description=description,
            category=category
            # created_by=request.user
        )

        messages.success(request, "Quiz created successfully")

        
        return redirect("add-questions", quiz_id=quiz.id)

    return render(request, "quize/add.html")


@login_required
@handle_object_not_found(Quiz, 'quiz_id')
def update_quiz_info(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == 'POST':
        # Get the updated data from the form
        title = request.POST.get('title')
        description = request.POST.get('description')

        if title and description:
            # Update the quiz info
            quiz.title = title
            quiz.description = description
            quiz.save()

            # Redirect to the quiz detail page or another page
            messages.success(request, "Quiz has been updated successfully")
        else:
            messages.error(request, "Both title and description are required")

    return redirect('quiz-detail', quiz_id=quiz.id)


@login_required
@handle_object_not_found(Quiz, 'quiz_id')
def publish_quiz(request, quiz_id):
    # Fetch the quiz object
    quiz = get_object_or_404(Quiz, id=quiz_id)
    redirect_view = request.GET.get('redirect')


    # Check if the quiz has at least 3 questions
    if quiz.questions.count() < 3:
        messages.error(request, "The quiz must have at least 3 question to be published.")
        if redirect_view in ['add-questions', 'quiz-detail']:
            return redirect(redirect_view, quiz_id=quiz.id)
        return redirect('add-questions', quiz_id=quiz.id)

    # Mark the quiz as published
    quiz.is_published = True
    quiz.save()
    messages.success(request, "Quiz has been published successfully!")
    return redirect("quiz-detail", quiz_id=quiz.id)  # Redirect to the quiz detail page


@login_required
@handle_object_not_found(Quiz, 'quiz_id')
def add_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        question_type = request.POST.get("question_type")

        if not question_text or not question_type:
            messages.error(request, "Question text and type are required.")
            return redirect("add-questions", quiz_id=quiz.id)

        question = Question.objects.create(
            quiz=quiz, question_text=question_text, question_type=question_type
        )

        if question_type in ["checkboxes", "radio"]:
            option_texts = request.POST.getlist("option_text[]")
            option_images = request.FILES.getlist("option_image[]")  # Retrieve uploaded images

            for idx, option_text in enumerate(option_texts):
                if option_text.strip():
                    QuestionOption.objects.create(
                        question=question,
                        text=option_text,
                        image=option_images[idx] if idx < len(option_images) else None,
                    )

        return redirect("add-questions", quiz_id=quiz.id)

    return render(
        request,
        "quize/add-question-new.html",
        {"quiz": quiz, "questions": quiz.questions.all()},
    )


@login_required
def edit_question(request, quiz_id, question_id):
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        question = get_object_or_404(Question, id=question_id, quiz=quiz)
    except Exception as e:
        messages.error(request, str(e))
        return redirect("quize_list")

    if request.method == "POST":
        # Update Question Basic Info
        question.question_text = request.POST.get("question_text")
        question.question_type = request.POST.get("question_type")
        question.save()

        # Manage Options
        submitted_ids = []
        for key in request.POST:
            if key.startswith("option_text-"):
                # Extract the ID from the key
                option_id = key.split("-")[1]
                submitted_ids.append(int(option_id))

        # Delete options not in submitted_ids
        for option in question.options.all():
            if option.id not in submitted_ids:
                option.delete()

        # Add new options
        new_texts = request.POST.getlist("option_text[]")
        new_images = request.FILES.getlist("option_image[]")

        for i, text in enumerate(new_texts):
            new_option = QuestionOption.objects.create(
                question=question, text=text
            )
            if i < len(new_images):
                new_option.image = new_images[i]
                new_option.save()

        messages.success(request, "Question updated successfully.")
        return redirect("quiz-detail", quiz_id=quiz.id)

    return render(request, "quize/edit-question.html", {"quiz": quiz, "question": question})


@login_required
def delete_question(request, quiz_id, question_id):
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        question = get_object_or_404(Question, id=question_id, quiz=quiz)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('quize_list')
    
    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect('quiz-detail', quiz_id=quiz_id)


@login_required
@handle_object_not_found(Quiz, 'quiz_id')
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    quiz.delete()
    messages.success(request, "Quiz has been deleted successfully.")
    return redirect('quize_list') 


@handle_object_not_found(Quiz, 'quiz_id')
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    context = {
        'quiz': quiz
    }
    return render(request, "quize/attempt-quiz.html", context)


@handle_object_not_found(Quiz, 'quiz_id')
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    context = {
        'quiz': quiz,
        'questions': quiz.questions.all()
    }
    return render(request, "quize/start-quiz.html", context)



@require_POST
@handle_object_not_found(Quiz, 'quiz_id')
def submit_quiz(request, quiz_id):
    import json
    # Get the quiz object
    quiz = Quiz.objects.get(id=quiz_id)

    # Check if the respondent exists (e.g., from a previous session or create a new one)
    email = request.POST.get('email')  # Assuming email is passed with the form data
    full_name = request.POST.get('full_name')
    respondent, created = Respondent.objects.get_or_create(
        email=email,
        defaults={'full_name': full_name},
    )

    # Create a new attempt for this quiz by the respondent
    attempt = Attempt.objects.create(quiz=quiz, respondent=respondent)

    # Loop through each question and save the responses
    for question in quiz.questions.all():
        # Get the answer or selected options
        answer = request.POST.get(f'question_{question.id}')  # This will be text or option ID(s)

        if question.question_type == 'radio':
            selected_option = request.POST.get(f'question_{question.id}')
            selected_option_objs = QuestionOption.objects.filter(id=selected_option)
            submitted_response = Response.objects.create(
                attempt=attempt,
                question=question
            )
            submitted_response.selected_option.add(*selected_option_objs)


        elif question.question_type == 'checkboxes':  # Multiple choice or single choice
            selected_options = request.POST.getlist(f'question_{question.id}[]')  # Multiple options for checkboxes
            
            # Find the selected options from the database
            selected_option_objs = QuestionOption.objects.filter(id__in=selected_options)

            # Create a Response record for each question
            submitted_response = Response.objects.create(
                attempt=attempt,
                question=question
            )

            submitted_response.selected_option.add(*selected_option_objs)
        
        else:
            Response.objects.create(
                attempt=attempt,
                question=question,
                answer=str(answer),
            )
        

    # Redirect to a results or success page (you can customize this as needed)
    messages.success(request, "Thanks for submitting the quiz, your Report is being generated.")
    return redirect('quiz-complete', attempt_id=attempt.id)


@handle_object_not_found(Attempt, 'attempt_id')
def quiz_results(request, attempt_id):
    context = {'attempt_id': attempt_id}
    return redirect('quiz-complete', attempt_id=attempt_id)
    return render(request, "quize/quiz-result.html", context)

@handle_object_not_found(Attempt, 'attempt_id')
def quiz_report(request, attempt_id):
    # Fetch the specific attempt (response) using the attempt_id
    attempt = get_object_or_404(Attempt, id=attempt_id)
    ai_output = attempt.get_ai_report()
   
    context = {
        'roadmap': ai_output
    }
    
    return render(request, "quize/quiz-report.html", context)


@handle_object_not_found(Attempt, 'attempt_id')
def quiz_attempt_detail(request, quiz_id, attempt_id):
    try:
        # Fetch the quiz object using the quiz_id
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Fetch the specific attempt (response) using the attempt_id
        attempt = get_object_or_404(Attempt, id=attempt_id, quiz=quiz)

    except Exception as e:
        messages.error(request, str(e))
        return redirect("quize_list")

    # Fetch all the questions and the corresponding answers for the attempt
    questions = quiz.questions.all()
    responses = attempt.responses.all()
    


    context = {
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'responses': responses,
    }
    
    return render(request, 'quize/attempt_detail.html', context)


def generate_ai_report(request):
    attempt_id = request.GET.get('attempt_id')
    
    if not attempt_id:
        return JsonResponse({"result": "Error: attempt_id parameter is required"}, status=400)
    
    # Fetch the Attempt object
    attempt = get_object_or_404(Attempt, id=attempt_id)
    
    # Generate the AI report (replace with your actual logic)
    ai_report = attempt.get_ai_report()  # This should return the AI result
    
    # Render the template with the data (ai_report or any other context)
    context = {'roadmap': ai_report}
    print(context)
    rendered_html = render_to_string('quize/quiz-report-wellness.html', context)  # Provide your template's name
    
    # Return the rendered HTML in a JSON response
    return JsonResponse({
        "result": rendered_html,
        "longevity_score": ai_report['longevity_score'],
    })



from django.http import StreamingHttpResponse
import time
import json


def sse_view(request, attempt_id):
    """
    SSE view to stream AI roadmap generation in real-time.
    """
    def event_stream():
        # Instantiate the AI roadmap generator with the attempt ID
        roadmap_generator = AIRoadmapGenerator(attempt_id=attempt_id)
        try:
            # Call the streaming method and yield responses
            for partial_content in roadmap_generator.generate_ai_response_streaming():
                # Directly stream the AI content
                yield f"data: {partial_content}\n\n"
        except Exception as e:
            # Handle any errors and send a termination signal
            error_data = {
                "type": "error",
                "message": str(e),
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    # Create the streaming response
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Allow Stream over NGINX server
    return response


@handle_object_not_found(Attempt, 'attempt_id')
def quiz_complete(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    context = {
        'attempt_id': attempt_id
    }
    messages.success(request, "Thanks for submitting the quiz, your Report is being generated.")
    return render(request, "quize/quiz-test.html", context)


def quiz_test(request):
    return render(request, "quize/quiz-test.html")



def get_products(request):
    # Query all products from the database
    products = Product.objects.all()

    # Prepare the JSON response
    response_data = {
        product.key: {
            "title": product.title,
            "thumbnail": product.thumbnail.url if product.thumbnail else None,
            "link": product.link,
        }
        for product in products
    }

    # Return the data as a JSON response
    return JsonResponse({"products": response_data}, safe=False)