from django.urls import path

from .api_views import (
    ActiveQuestionnaireListAPIView,
    PaymentListAPIView,
    QuestionnaireDetailAPIView,
    QuestionnaireResponseCreateAPIView,
    TeamListAPIView,
    TeamMembersAPIView,
    TrainingListAPIView,
)

app_name = "team_api"

urlpatterns = [
    path("teams/", TeamListAPIView.as_view(), name="team_list"),
    path("teams/<int:team_id>/members/", TeamMembersAPIView.as_view(), name="team_members"),
    path("trainings/", TrainingListAPIView.as_view(), name="training_list"),
    path("payments/", PaymentListAPIView.as_view(), name="payment_list"),
    path("questionnaires/active/", ActiveQuestionnaireListAPIView.as_view(), name="questionnaire_active_list"),
    path("questionnaires/<int:pk>/detail/", QuestionnaireDetailAPIView.as_view(), name="questionnaire_detail"),
    path("questionnaire-responses/", QuestionnaireResponseCreateAPIView.as_view(), name="questionnaire_response_create"),
]
