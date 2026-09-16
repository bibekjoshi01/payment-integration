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

# Shared one-time checkout API. Legacy URLs above remain available.
from .views import ConfigView, PaymentCreateView, PaymentDetailView, PaymentVerifyView, PaymentSimulateView
from .webhooks import WebhookView

urlpatterns += [
    path('config', ConfigView.as_view(), name='checkout-config'),
    path('payments', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<uuid:payment_id>', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<uuid:payment_id>/verify', PaymentVerifyView.as_view(), name='payment-verify'),
    path('payments/<uuid:payment_id>/simulate', PaymentSimulateView.as_view(), name='payment-simulate'),
    path('webhooks/<str:gateway>', WebhookView.as_view(), name='payment-webhook'),
]
