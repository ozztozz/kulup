from django.urls import path

from .api_views import StartListImportAPIView

app_name = "result_api"

urlpatterns = [
    path("results/start-list/import/", StartListImportAPIView.as_view(), name="start_list_import"),
]
