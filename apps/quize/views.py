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



class QuizeListView(View):
    template_name = "quize/list.html"

    def get(self, request, *args, **kwargs):

        context = {}
        return render(request, self.template_name, context=context)


class QuizeAddView(View):
    template_name = "quize/add.html"

    def get(self, request, *args, **kwargs):

        context = {}
        return render(request, self.template_name, context=context)