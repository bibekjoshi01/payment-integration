"""PayPal sandbox Orders v2: create, approve, capture, then verify captures."""
from django.conf import settings

from .common import GatewayError, checkout_url, confirmed, major, request, return_url, to_minor

BASE_URL = 'https://api-m.sandbox.paypal.com'


def headers():
    token = request('POST', f'{BASE_URL}/v1/oauth2/token',
                    auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
                    data={'grant_type': 'client_credentials'})
    if not token.get('access_token'):
        raise GatewayError()
    return {'Authorization': f"Bearer {token['access_token']}", 'Content-Type': 'application/json'}


def create(payment):
    auth = headers()
    auth['PayPal-Request-Id'] = str(payment.id)
    data = request('POST', f'{BASE_URL}/v2/checkout/orders', headers=auth, json={
        'intent': 'CAPTURE',
        'purchase_units': [{'custom_id': str(payment.id), 'amount': {
            'currency_code': payment.currency, 'value': major(payment),
        }}],
        'payment_source': {'paypal': {'experience_context': {
            'return_url': return_url(payment), 'cancel_url': return_url(payment) + '?cancelled=1',
            'user_action': 'PAY_NOW', 'shipping_preference': 'NO_SHIPPING',
        }}},
    })
    link = next((item['href'] for item in data.get('links', []) if item.get('rel') in {'payer-action', 'approve'}), '')
    return data['id'], checkout_url(link, {'www.sandbox.paypal.com', 'sandbox.paypal.com'})


def verify(payment, transaction_id=None):
    auth = headers()
    url = f'{BASE_URL}/v2/checkout/orders/{payment.provider_id}'
    data = request('GET', url, headers=auth)
    units = data.get('purchase_units', [])
    if data.get('id') != payment.provider_id or len(units) != 1:
        raise GatewayError('Unexpected PayPal order.')
    unit = units[0]
    confirmed(payment, 'paid', to_minor(unit.get('amount', {}).get('value')),
              unit.get('amount', {}).get('currency_code'), unit.get('custom_id'))
    if data.get('status') == 'APPROVED':
        auth['PayPal-Request-Id'] = f'{payment.id}-capture'
        try:
            request('POST', url + '/capture', headers=auth, json={})
        except GatewayError:
            # Another callback may have captured it already. Re-query before failing.
            current = request('GET', url, headers=auth)
            if current.get('status') != 'COMPLETED':
                raise
        data = request('GET', url, headers=auth)
    if data.get('status') != 'COMPLETED':
        return 'failed' if data.get('status') == 'VOIDED' else 'pending'
    unit = data['purchase_units'][0]
    captures = unit.get('payments', {}).get('captures', [])
    if not captures or any(c.get('status') != 'COMPLETED' for c in captures):
        return 'pending'
    if any(c.get('amount', {}).get('currency_code') != payment.currency for c in captures):
        raise GatewayError('Unexpected PayPal capture currency.')
    total = sum(to_minor(c.get('amount', {}).get('value')) for c in captures)
    return confirmed(payment, 'paid', total, payment.currency, unit.get('custom_id'))
