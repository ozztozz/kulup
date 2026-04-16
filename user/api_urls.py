from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_views import MeAPIView, UserListAPIView

app_name = "user_api"

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeAPIView.as_view(), name="me"),
    path("users/", UserListAPIView.as_view(), name="user_list"),
]
