from django.urls import path

<<<<<<< HEAD
from .api_views import StartListImportAPIView,ResultImportAPIView
=======
from .api_views import StartListImportAPIView
from .api_views import (
    StartListClubListAPIView,
    StartListEntryListAPIView,
    StartListEventListAPIView,
    StartListItemListAPIView,
)
>>>>>>> b5956502a06b6e54593360a553dceb25c1ffa2ac

app_name = "result_api"

urlpatterns = [
    path("results/start-list/import/", StartListImportAPIView.as_view(), name="start_list_import"),
<<<<<<< HEAD
    path("results/results/import/", ResultImportAPIView.as_view(), name="result_import"),
=======
    path("results/start-list/events/", StartListEventListAPIView.as_view(), name="start_list_events"),
    path("results/start-list/clubs/", StartListClubListAPIView.as_view(), name="start_list_clubs"),
    path("results/start-list/items/", StartListItemListAPIView.as_view(), name="start_list_items"),
    path("results/start-list/entries/", StartListEntryListAPIView.as_view(), name="start_list_entries"),
>>>>>>> b5956502a06b6e54593360a553dceb25c1ffa2ac
]
