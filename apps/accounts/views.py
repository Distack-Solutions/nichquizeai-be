from django.shortcuts import render
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
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_path = request.POST.get("next")
            if next_path:
                return redirect(next_path)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



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
    return redirect('login')


def test(request):
    context = {
        "active_id" : cache.get('active_id', 1)
    }
    if request.method == 'POST':
        active = request.POST.get('active')
        print()
        cache.set('active_id', 2)
        return redirect('test')
    return render(request, "test.html", context=context)
