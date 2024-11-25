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



class DashboardView(View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):

        context = {}
        return render(request, self.template_name, context=context)
    


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