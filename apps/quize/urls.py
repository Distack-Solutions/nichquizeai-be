from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.QuizeListView.as_view(),
        name="quize_list",
    ),
    path(
        "add/",
        views.QuizeAddView.as_view(),
        name="quize_add",
    ),
]
