"""A shared payment lifecycle; adapters handle only provider-specific details."""

import uuid

from django.conf import settings
from django.db import OperationalError, transaction
from django.utils import timezone
from rest_framework.exceptions import APIException, NotFound, ValidationError

from .catalog import CURRENCIES, PRODUCTS
from .models import Payment
from .providers import get_provider
from .providers.common import GatewayError


class Conflict(APIException):
    status_code = 409


def create_payment(data, key):
    try:
        key = uuid.UUID(str(key))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValidationError("Send a UUID in the Idempotency-Key header.") from exc
    gateway = data["gateway"]
    currency = CURRENCIES[gateway]
    # Persist before contacting the provider, so an uncertain response can be retried
    # with the same saved reference and upstream idempotency key.
    payment, _ = Payment.objects.get_or_create(
        idempotency_key=key,
        defaults={
            **data,
            "mode": settings.PAYMENT_MODE,
            "currency": currency,
            "amount_minor": PRODUCTS[data["product"]]["prices"][currency],
        },
    )
    if any(
        getattr(payment, field) != value
        for field, value in {**data, "mode": settings.PAYMENT_MODE}.items()
    ):
        raise Conflict("This idempotency key belongs to a different checkout.")
    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(pk=payment.pk)
            if payment.checkout_url:
                return payment
            if payment.mode == "mock":
                payment.provider_id = f"mock-{payment.id}"
                payment.checkout_url = (
                    f"{settings.FRONTEND_BASE_URL}/simulate/{payment.id}"
                )
            else:
                try:
                    payment.provider_id, payment.checkout_url = get_provider(
                        gateway
                    ).create(payment)
                except (KeyError, TypeError, IndexError) as exc:
                    raise GatewayError(
                        "Provider returned an incomplete checkout response."
                    ) from exc
            payment.save(update_fields=["provider_id", "checkout_url", "updated_at"])
    except OperationalError as exc:
        raise Conflict(
            "Another checkout request is running. Retry with the same idempotency key."
        ) from exc
    return payment


def find_payment(payment_id):
    try:
        return Payment.objects.get(pk=payment_id)
    except Payment.DoesNotExist as exc:
        raise NotFound("Payment not found.") from exc


def set_status(payment, state):
    # Conditional update prevents a late pending/failed result from overwriting paid.
    Payment.objects.filter(pk=payment.pk).exclude(status="paid").update(
        status=state, updated_at=timezone.now()
    )
    payment.refresh_from_db()
    return payment


def verify_payment(payment, transaction_id=None):
    if payment.mode != settings.PAYMENT_MODE:
        raise Conflict(
            "Restart in the mode used to create this payment before verifying it."
        )
    if payment.mode == "mock" or payment.status == "paid":
        return payment
    if not payment.provider_id:
        raise Conflict(
            "Checkout creation is incomplete. Retry the original checkout request."
        )
    try:
        state = get_provider(payment.gateway).verify(payment, transaction_id)
    except (KeyError, TypeError, IndexError) as exc:
        raise GatewayError(
            "Provider returned an incomplete verification response."
        ) from exc
    return set_status(payment, state)
