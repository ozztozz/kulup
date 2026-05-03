from django.urls import path

from .api_views import StartListImportAPIView,ResultImportAPIView

app_name = "result_api"

urlpatterns = [
    path("results/start-list/import/", StartListImportAPIView.as_view(), name="start_list_import"),
    path("results/results/import/", ResultImportAPIView.as_view(), name="result_import"),
]
