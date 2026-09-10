"""Stripe hosted Checkout in payment mode, with server-side session retrieval."""
from django.conf import settings

from .common import GatewayError, checkout_url, confirmed, request, return_url

BASE_URL = 'https://api.stripe.com/v1'


def headers():
    return {'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'}


def create(payment):
    auth = headers()
    auth['Idempotency-Key'] = str(payment.id)
    data = request('POST', f'{BASE_URL}/checkout/sessions', headers=auth, data={
        'mode': 'payment', 'customer_email': payment.email,
        'client_reference_id': str(payment.id), 'metadata[payment_id]': str(payment.id),
        'payment_method_types[0]': 'card',
        'line_items[0][price_data][currency]': payment.currency.lower(),
        'line_items[0][price_data][unit_amount]': payment.amount_minor,
        'line_items[0][price_data][product_data][name]': 'Payment integration guide',
        'line_items[0][quantity]': 1,
        'success_url': return_url(payment),
        'cancel_url': return_url(payment) + '?cancelled=1',
    })
    return data['id'], checkout_url(data.get('url'), {'checkout.stripe.com'})


def verify(payment, transaction_id=None):
    data = request('GET', f'{BASE_URL}/checkout/sessions/{payment.provider_id}', headers=headers())
    if data.get('id') != payment.provider_id or data.get('livemode') is not False or data.get('mode') != 'payment':
        raise GatewayError('Unexpected Stripe sandbox session.')
    state = 'paid' if data.get('payment_status') == 'paid' else 'pending'
    if state != 'paid' and data.get('status') == 'expired':
        state = 'failed'
    return confirmed(payment, state, data.get('amount_total'), data.get('currency'), data.get('client_reference_id'))
