from django.urls import path
from .views import RetrieveSessionView, SubscribePlanAPIView, SubscriptionPlanListAPIView

urlpatterns = [
    path(
        "subscription-plans",
        SubscriptionPlanListAPIView.as_view(),
        name="subscription-plan-list",
    ),
    path("subscribe", SubscribePlanAPIView.as_view(), name="subscribe-plan"),
    path("verify/<str:session_id>", RetrieveSessionView.as_view(), name="subscription-verify"),
]
