"""Authenticate raw webhook bodies, then re-query providers before changing state."""
import hashlib
import hmac
import json
import uuid

import stripe
from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .models import Payment, WebhookReceipt
from .providers import paypal
from .providers.common import NotConfigured, request, require
from .services import verify_payment
from .views import PublicView


def validate_signature(gateway, body, headers, event):
    require(gateway)
    if gateway == 'stripe':
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise NotConfigured('Set STRIPE_WEBHOOK_SECRET before receiving webhooks.')
        try:
            stripe.Webhook.construct_event(body, headers.get('Stripe-Signature', ''), settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.SignatureVerificationError) as exc:
            raise ValidationError('Invalid webhook signature.') from exc
    elif gateway == 'paystack':
        expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(), body, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(expected, headers.get('x-paystack-signature', '')):
            raise ValidationError('Invalid webhook signature.')
    elif gateway == 'flutterwave':
        secret = settings.FLUTTERWAVE_WEBHOOK_SECRET
        if not secret:
            raise NotConfigured('Set FLUTTERWAVE_WEBHOOK_SECRET before receiving webhooks.')
        if not hmac.compare_digest(secret, headers.get('verif-hash', '')):
            raise ValidationError('Invalid webhook secret hash.')
    elif gateway == 'paypal':
        if not settings.PAYPAL_WEBHOOK_ID:
            raise NotConfigured('Set PAYPAL_WEBHOOK_ID before receiving webhooks.')
        names = {'auth_algo': 'PAYPAL-AUTH-ALGO', 'cert_url': 'PAYPAL-CERT-URL',
                 'transmission_id': 'PAYPAL-TRANSMISSION-ID', 'transmission_sig': 'PAYPAL-TRANSMISSION-SIG',
                 'transmission_time': 'PAYPAL-TRANSMISSION-TIME'}
        payload = {key: headers.get(header, '') for key, header in names.items()}
        if not all(payload.values()):
            raise ValidationError('Missing PayPal transmission headers.')
        result = request('POST', f'{paypal.BASE_URL}/v1/notifications/verify-webhook-signature',
                         headers=paypal.headers(), json={**payload, 'webhook_id': settings.PAYPAL_WEBHOOK_ID, 'webhook_event': event})
        if result.get('verification_status') != 'SUCCESS':
            raise ValidationError('Invalid webhook signature.')


def event_target(gateway, event):
    """Return event key plus a provider ID or local reference for supported events."""
    if gateway == 'stripe':
        if event.get('type') not in {'checkout.session.completed', 'checkout.session.async_payment_succeeded',
                                     'checkout.session.async_payment_failed', 'checkout.session.expired'}:
            return None
        return str(event['id']), 'provider_id', str(event['data']['object']['id']), None
    if gateway == 'paystack':
        if event.get('event') != 'charge.success':
            return None
        data = event['data']
        return f"charge.success:{data['id']}", 'id', str(data['reference']), None
    if gateway == 'flutterwave':
        if event.get('event') != 'charge.completed':
            return None
        data = event['data']
        return f"charge.completed:{data['id']}:{data['status']}", 'id', str(data['tx_ref']), str(data['id'])
    if gateway == 'paypal':
        if event.get('event_type') not in {'CHECKOUT.ORDER.APPROVED', 'PAYMENT.CAPTURE.COMPLETED'}:
            return None
        resource = event['resource']
        provider_id = resource['id'] if event['event_type'] == 'CHECKOUT.ORDER.APPROVED' else resource['supplementary_data']['related_ids']['order_id']
        return str(event['id']), 'provider_id', str(provider_id), None


class WebhookView(PublicView):
    def post(self, request, gateway):
        if gateway not in {'stripe', 'paypal', 'paystack', 'flutterwave'} or settings.PAYMENT_MODE != 'sandbox':
            raise NotFound('Sandbox webhook endpoint is unavailable.')
        body = request.body
        try:
            event = json.loads(body)
            if not isinstance(event, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValidationError('Expected a JSON event object.') from exc
        validate_signature(gateway, body, request.headers, event)
        try:
            target = event_target(gateway, event)
        except (KeyError, TypeError) as exc:
            raise ValidationError('Incomplete webhook event.') from exc
        if target is None:
            return Response({'received': True, 'ignored': True})
        event_id, field, value, transaction_id = target
        if not event_id or len(event_id) > 255:
            raise ValidationError('Invalid event ID.')
        if field == 'id':
            try:
                uuid.UUID(value)
            except (ValueError, TypeError) as exc:
                raise ValidationError('Invalid payment reference.') from exc
        payment = Payment.objects.filter(gateway=gateway, mode='sandbox', **{field: value}).first()
        if not payment:
            # Do not acknowledge a race with checkout creation: let the provider retry.
            return Response({'detail': 'No matching saved payment yet.'}, status=503)
        with transaction.atomic():
            _, created = WebhookReceipt.objects.get_or_create(gateway=gateway, event_id=event_id)
            if created:
                verify_payment(payment, transaction_id)
            # An upstream failure rolls back the receipt so delivery can be retried.
        return Response({'received': True, 'duplicate': not created})
