from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.DashboardView.as_view(),
        name="home",
    ),
    path(
        "login/",
        views.login_view,
        name="login",
    ),
    path(
        "signup/",
        views.signup_view,
        name="signup",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("test/<uuid:id>/", views.test, name="test"),
    path("test/report/<int:id>/", views.test_report, name="test_report"),
]
