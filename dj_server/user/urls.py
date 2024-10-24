from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserLoginView,
    UserSignUpAPIView,
)

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path(
        "users/signup",
        UserSignUpAPIView.as_view(),
        name="user_signup",
    ),
    path("users/login", UserLoginView.as_view(), name="user_login"),
    path("", include(router.urls)),
]
