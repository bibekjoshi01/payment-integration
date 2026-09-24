from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import requests
from django.conf import settings
from rest_framework.exceptions import APIException


class GatewayError(APIException):
    status_code = 502
    default_detail = "The payment provider could not complete this request. Try checking the payment status again."


class NotConfigured(APIException):
    status_code = 503
    default_detail = "Configure this provider with sandbox credentials in dj_server/.env and restart the backend."


def request(method, url, **kwargs):
    try:
        response = requests.request(
            method, url, timeout=settings.PROVIDER_TIMEOUT, **kwargs
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Expected object")
        return data
    except (requests.RequestException, ValueError) as exc:
        # Never send upstream bodies, tokens or customer details to the client.
        raise GatewayError() from exc


def return_url(payment):
    return f"{settings.FRONTEND_BASE_URL}/return/{payment.id}"


def checkout_url(url, hosts):
    parsed = urlparse(url or "")
    if (
        parsed.scheme != "https"
        or parsed.hostname not in hosts
        or parsed.username
        or parsed.password
    ):
        raise GatewayError("Provider returned an unexpected checkout URL.")
    return url


def major(payment):
    return f"{Decimal(payment.amount_minor) / 100:.2f}"


def confirmed(payment, state, amount_minor, currency, reference):
    if state != "paid":
        return state
    try:
        amount = Decimal(str(amount_minor))
        valid = amount.is_finite() and amount == payment.amount_minor
    except (InvalidOperation, TypeError, ValueError):
        valid = False
    if (
        not valid
        or str(currency).upper() != payment.currency
        or str(reference) != str(payment.id)
    ):
        raise GatewayError(
            "Payment details do not match the saved order. No payment was confirmed."
        )
    return "paid"


def to_minor(amount):
    try:
        return Decimal(str(amount)) * 100
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise GatewayError("Provider returned an invalid amount.") from exc


def require(gateway):
    if gateway == "paypal":
        valid = settings.PAYPAL_CLIENT_ID and settings.PAYPAL_CLIENT_SECRET
    else:
        key, prefix = {
            "stripe": (settings.STRIPE_SECRET_KEY, "sk_test_"),
            "paystack": (settings.PAYSTACK_SECRET_KEY, "sk_test_"),
            "flutterwave": (settings.FLUTTERWAVE_SECRET_KEY, "FLWSECK_TEST-"),
        }[gateway]
        valid = key.startswith(prefix) and len(key) > len(prefix)
    if not valid:
        raise NotConfigured()
