from django.urls import path

from .views import startlist_page, htmx_club_list, htmx_swimmer_list, htmx_result_list

app_name = "result"

urlpatterns = [
    path("", startlist_page, name="startlist_page"),
    path("htmx/club-list/", htmx_club_list, name="htmx_club_list"),
    path("htmx/swimmer-list/", htmx_swimmer_list, name="htmx_swimmer_list"),
    path("htmx/result-list/", htmx_result_list, name="htmx_result_list"),
]
