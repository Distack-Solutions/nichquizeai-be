from django.urls import reverse

from django.shortcuts import render, redirect

# forms
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm

# utils
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.cache import cache


class DashboardView(View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):

        context = {}
        return render(request, self.template_name, context=context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_path = request.POST.get("next")
            if next_path:
                return redirect(next_path)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def signup_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    form = UserRegistrationForm(request.POST or None)
    context = {"form": form, "next": next_url}
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")

    return render(request, "sign_up.html", context=context)


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


#
from apps.quize.models import Quiz, Question, QuestionOption, Respondent, Attempt, Response
import json


def test(request, id):
    quiz = Quiz.objects.get(id=id)
    questions = Question.objects.filter(quiz=quiz)
    question_set = []
    for question in questions:
        info_data = {}
        info_data["id"] = question.id
        info_data["title"] = question.question_text
        info_data["type"] = question.question_type
        options = QuestionOption.objects.filter(question=question).values(
            "id", "text", "image"
        )
        info_data["options"] = list(options)
        question_set.append(info_data)
   
    context = {
        "active_id": cache.get("active_id", 1),
        "quiz": quiz,
        "question_set": json.dumps(question_set),
    }
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        data = request.POST.get("data")
        response_data = json.loads(data)

        respondent, create = Respondent.objects.get_or_create(
            email=email, defaults={"full_name": full_name}
        )

        # Attempt
        attempt = Attempt.objects.create(quiz=quiz, respondent=respondent)

        for ans in response_data:
            question = Question.objects.get(id=ans.get("id"))

            if ans.get("type") == "text":
                response = Response.objects.create(question=question, attempt=attempt)
                answer = ans.get("answer")
                response.answer = answer

            elif ans.get("type") == "radio":
                selected_option = QuestionOption.objects.filter(
                    id__in=ans.get("selected_option")
                )
                response.selected_option.set(selected_option) 

            response.save()
        url = reverse('test', kwargs={'id': id})
        return redirect(f"{url}?status=success")
    return render(request, "test.html", context=context)
