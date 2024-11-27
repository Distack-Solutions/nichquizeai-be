from django.urls import path
from . import views

urlpatterns = [
    path(
        "quiz",
        views.QuizListView.as_view(),
        name="quize_list",
    ),
    path(
        "quiz/add/",
        views.create_quiz,
        name="add-quiz",
    ),

    path(
        'quiz/<quiz_id>/add-questions',
        views.add_questions,
        name="add-questions"
    ),

    path('quiz/<uuid:quiz_id>/publish/', views.publish_quiz, name='publish-quiz'),
    path('quiz/<uuid:quiz_id>/', views.quiz_detail, name='quiz-detail'),
    path('quiz/<uuid:quiz_id>/update', views.update_quiz_info, name='update-quiz-info'),
    path('quiz/<uuid:quiz_id>/questions/<int:question_id>/edit', views.edit_question, name='edit-question'),
    path('quiz/<uuid:quiz_id>/question/<int:question_id>/delete/', views.delete_question, name='delete-question'),

    path('quiz/<uuid:quiz_id>/delete/', views.delete_quiz, name='delete-quiz'),


    path('quiz/<uuid:quiz_id>/attempt/', views.attempt_quiz, name='attempt-quiz'),
    path('quiz/<uuid:quiz_id>/attempt/start', views.start_quiz, name='start-quiz'),
    path('quiz/<uuid:quiz_id>/attempt/submit', views.submit_quiz, name='submit-quiz'),

    path('quiz/attempt/<uuid:attempt_id>/result', views.quiz_results, name='quiz-results'),

    path('quiz/<uuid:quiz_id>/attempt/<uuid:attempt_id>/', views.quiz_attempt_detail, name='quiz-attempt-detail'),

]

