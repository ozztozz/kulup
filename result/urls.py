from django.urls import path

from .views import startlist_page, htmx_club_list

app_name = "result"

urlpatterns = [
    path("", startlist_page, name="startlist_page"),
    path("htmx/club-list/", htmx_club_list, name="htmx_club_list"),
]
