"""
URL configuration for dj_server project.
"""

from django.contrib import admin
from django.urls import path, include
from .views import CreateOrderView, CaptureOrderView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth", include("rest_framework.urls")),
    path("api/orders", CreateOrderView.as_view(), name="create-order"),
    path(
        "api/orders/<str:orderID>/capture",
        CaptureOrderView.as_view(),
        name="capture-order",
    ),
    path("api/user-app/", include("user.urls"), name="user-app"),
    path(
        "api/subscription-app/", include("subscription.urls"), name="subscription-app"
    ),
]
