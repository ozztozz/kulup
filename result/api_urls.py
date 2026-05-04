from django.urls import path

from .api_views import StartListImportAPIView,ResultImportAPIView
from .api_views import (
    StartListClubListAPIView,
    StartListEntryListAPIView,
    StartListEventListAPIView,
    StartListItemListAPIView,
    LastResultListAPIView,
)

app_name = "result_api"

urlpatterns = [
    path("results/start-list/import/", StartListImportAPIView.as_view(), name="start_list_import"),
    path("results/start-list/events/", StartListEventListAPIView.as_view(), name="start_list_events"),
    path("results/start-list/clubs/", StartListClubListAPIView.as_view(), name="start_list_clubs"),
    path("results/start-list/items/", StartListItemListAPIView.as_view(), name="start_list_items"),
    path("results/start-list/entries/", StartListEntryListAPIView.as_view(), name="start_list_entries"),
    path("results/results/import/", ResultImportAPIView.as_view(), name="result_import"),
    path("results/last-results/", LastResultListAPIView.as_view(), name="last_results"),
]
