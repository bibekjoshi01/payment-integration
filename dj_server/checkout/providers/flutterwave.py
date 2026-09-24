"""Flutterwave v3 Standard hosted checkout and transaction verification."""

import hashlib

from django.conf import settings

from .common import (
    GatewayError,
    checkout_url,
    confirmed,
    major,
    request,
    return_url,
    to_minor,
)

BASE_URL = "https://api.flutterwave.com/v3"


def headers():
    return {"Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"}


def create(payment):
    secret_hash = hashlib.sha256(settings.FLUTTERWAVE_SECRET_KEY.encode()).hexdigest()
    checksum = hashlib.sha256(
        f"{major(payment)}{payment.currency}{payment.email}{payment.id}{secret_hash}".encode()
    ).hexdigest()
    result = request(
        "POST",
        f"{BASE_URL}/payments",
        headers=headers(),
        json={
            "tx_ref": str(payment.id),
            "amount": major(payment),
            "currency": payment.currency,
            "redirect_url": return_url(payment),
            "customer": {"email": payment.email},
            "customizations": {"title": "Payment integration guide"},
            "payload_hash": checksum,
        },
    )
    if result.get("status") != "success":
        raise GatewayError()
    return str(payment.id), checkout_url(
        result["data"].get("link"), {"checkout.flutterwave.com"}
    )


def verify(payment, transaction_id=None):
    # Verification by reference also works when the browser never returns.
    result = request(
        "GET",
        f"{BASE_URL}/transactions/verify_by_reference",
        headers=headers(),
        params={"tx_ref": str(payment.id)},
    )
    if result.get("status") != "success":
        raise GatewayError()
    data = result["data"]
    if transaction_id and str(data.get("id")) != str(transaction_id):
        raise GatewayError("Flutterwave transaction ID does not match this order.")
    state = {"successful": "paid", "failed": "failed"}.get(
        data.get("status"), "pending"
    )
    return confirmed(
        payment,
        state,
        to_minor(data.get("amount")),
        data.get("currency"),
        data.get("tx_ref"),
    )
