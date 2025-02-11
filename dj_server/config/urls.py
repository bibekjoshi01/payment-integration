"""
URL configuration for dj_server project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth", include("rest_framework.urls")),
    path("api/user-app/", include("user.urls"), name="user-app"),
    path(
        "api/subscription/", include("subscription.urls"), name="subscription"
    ),
    # Checkout
    path("api/checkout/", include("checkout.urls"), name="checkout"),
]
