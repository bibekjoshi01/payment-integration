from django.urls import path

from .paystack import PayStackInitializePaymentView, PayStackVerifyPaymentView
from .paypal import CreateOrderView, CaptureOrderView

urlpatterns = [
    # PayStack
    path(
        "paystack/initiate-payment",
        PayStackInitializePaymentView.as_view(),
        name="initialize-payment",
    ),
    path(
        "paystack/verify-payment/<str:reference>",
        PayStackVerifyPaymentView.as_view(),
        name="verify-payment",
    ),
    # PayPal
    path("paypal/orders", CreateOrderView.as_view(), name="create-order"),
    path(
        "paypal/orders/<str:orderID>/capture",
        CaptureOrderView.as_view(),
        name="capture-order",
    ),
]
