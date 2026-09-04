from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CurrentUserView,
    RegisterView,
)


urlpatterns = [

    # Registration
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # Login
    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    # JWT token refresh
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # Current authenticated user
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),
]