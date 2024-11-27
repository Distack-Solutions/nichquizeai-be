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
from apps.quize.models import *

from django.db.models.functions import TruncDay
from django.db.models import Count

def dashboard(request):
    total_quizzes = Quiz.objects.count()
    published_quizzes = Quiz.objects.filter(is_published=True).count()
    total_respondents = Respondent.objects.count()
    total_attempts = Attempt.objects.count()
    recent_attempts = Attempt.objects.order_by('-created_at')[:5]
    
    # Group attempts by date
    attempts_by_date = (
        Attempt.objects.annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    
    # Prepare data for the chart
    chart_labels = [entry['day'].strftime('%d %b') for entry in attempts_by_date]
    chart_data = [entry['total'] for entry in attempts_by_date]

    context = {
        'total_quizzes': total_quizzes,
        'published_quizzes': published_quizzes,
        'total_respondents': total_respondents,
        'total_attempts': total_attempts,
        'recent_attempts': recent_attempts,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'index.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:home")
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_path = request.POST.get("next")
            if next_path:
                return redirect(next_path)
            return redirect('accounts:home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})