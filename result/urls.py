from django.urls import path

from .views import startlist_page

app_name = "result"

urlpatterns = [
    path("", startlist_page, name="startlist_page"),
]
