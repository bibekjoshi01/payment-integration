"""Paystack hosted transactions, using kobo on both initialize and verify."""

from django.conf import settings

from .common import GatewayError, checkout_url, confirmed, request, return_url

BASE_URL = "https://api.paystack.co"


def headers():
    return {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}


def create(payment):
    result = request(
        "POST",
        f"{BASE_URL}/transaction/initialize",
        headers=headers(),
        json={
            "email": payment.email,
            "amount": payment.amount_minor,
            "currency": payment.currency,
            "reference": str(payment.id),
            "callback_url": return_url(payment),
        },
    )
    if result.get("status") is not True:
        raise GatewayError()
    data = result["data"]
    if data.get("reference") != str(payment.id):
        raise GatewayError("Unexpected Paystack reference.")
    return data["reference"], checkout_url(
        data.get("authorization_url"), {"checkout.paystack.com"}
    )


def verify(payment, transaction_id=None):
    result = request(
        "GET", f"{BASE_URL}/transaction/verify/{payment.id}", headers=headers()
    )
    if result.get("status") is not True:
        raise GatewayError()
    data = result["data"]
    if data.get("domain") != "test":
        raise GatewayError("Expected a Paystack test transaction.")
    state = {"success": "paid", "failed": "failed", "abandoned": "failed"}.get(
        data.get("status"), "pending"
    )
    return confirmed(
        payment, state, data.get("amount"), data.get("currency"), data.get("reference")
    )
