import hashlib
import hmac
import json
import time
import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from checkout.models import Payment, WebhookReceipt
from checkout.providers.common import GatewayError

ROOT = '/api/checkout/webhooks'


@override_settings(PAYMENT_MODE='sandbox', PAYSTACK_SECRET_KEY='sk_test_example', STRIPE_SECRET_KEY='sk_test_example',
                   STRIPE_WEBHOOK_SECRET='whsec_example', FLUTTERWAVE_SECRET_KEY='FLWSECK_TEST-example',
                   FLUTTERWAVE_WEBHOOK_SECRET='webhook-example', PAYPAL_CLIENT_ID='sandbox-example',
                   PAYPAL_CLIENT_SECRET='sandbox-example', PAYPAL_WEBHOOK_ID='WH-example')
class WebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def payment(self, gateway):
        return Payment.objects.create(idempotency_key=uuid.uuid4(), gateway=gateway, mode='sandbox', product='demo-guide',
                                      email='buyer@example.com', amount_minor=1000, currency='USD', provider_id=f'{gateway}-session')

    def send(self, gateway, event, valid=True, timestamp=None):
        raw = json.dumps(event).encode()
        headers = {}
        if gateway == 'paystack':
            headers['HTTP_X_PAYSTACK_SIGNATURE'] = hmac.new(b'sk_test_example', raw, hashlib.sha512).hexdigest() if valid else 'invalid'
        elif gateway == 'stripe':
            timestamp = timestamp if timestamp is not None else int(time.time())
            signature = hmac.new(b'whsec_example', str(timestamp).encode() + b'.' + raw, hashlib.sha256).hexdigest()
            headers['HTTP_STRIPE_SIGNATURE'] = f't={timestamp},v1={signature}' if valid else 'invalid'
        elif gateway == 'flutterwave':
            headers['HTTP_VERIF_HASH'] = 'webhook-example' if valid else 'invalid'
        elif gateway == 'paypal' and valid:
            headers = {f'HTTP_PAYPAL_{key}': 'example' for key in ['AUTH_ALGO', 'CERT_URL', 'TRANSMISSION_ID', 'TRANSMISSION_SIG', 'TRANSMISSION_TIME']}
        return self.client.post(f'{ROOT}/{gateway}', raw, content_type='application/json', **headers)

    def test_paystack_duplicate_delivery_verifies_only_once(self):
        p = self.payment('paystack')
        event = {'event': 'charge.success', 'data': {'id': 11, 'reference': str(p.id)}}
        with patch('checkout.providers.paystack.verify', return_value='paid') as verify:
            self.assertEqual(self.send('paystack', event).status_code, 200)
            self.assertTrue(self.send('paystack', event).json()['duplicate'])
            self.assertEqual(verify.call_count, 1)
        p.refresh_from_db()
        self.assertEqual(p.status, 'paid')
        self.assertEqual(WebhookReceipt.objects.count(), 1)

    def test_verification_failure_rolls_back_receipt_for_retry(self):
        p = self.payment('paystack')
        event = {'event': 'charge.success', 'data': {'id': 11, 'reference': str(p.id)}}
        with patch('checkout.providers.paystack.verify', side_effect=GatewayError()):
            self.assertEqual(self.send('paystack', event).status_code, 502)
        self.assertEqual(WebhookReceipt.objects.count(), 0)
        p.refresh_from_db()
        self.assertEqual(p.status, 'pending')
        with patch('checkout.providers.paystack.verify', return_value='paid'):
            self.assertEqual(self.send('paystack', event).status_code, 200)

    def test_stripe_signed_event_requeries_session(self):
        p = self.payment('stripe')
        event = {'id': 'evt_example', 'type': 'checkout.session.completed', 'data': {'object': {'id': p.provider_id, 'payment_status': 'paid'}}}
        with patch('checkout.providers.stripe.verify', return_value='pending') as verify:
            self.assertEqual(self.send('stripe', event).status_code, 200)
            self.assertEqual(verify.call_count, 1)
        p.refresh_from_db()
        self.assertEqual(p.status, 'pending', 'Webhook payload alone must never confirm payment')

    def test_expired_or_invalid_signatures_are_rejected_for_all_gateways(self):
        with patch('checkout.services.get_provider') as provider:
            for gateway in ['stripe', 'paystack', 'flutterwave', 'paypal']:
                with self.subTest(gateway=gateway):
                    self.assertEqual(self.send(gateway, {}, valid=False).status_code, 400)
            self.assertEqual(self.send('stripe', {'type': 'ignored'}, timestamp=int(time.time()) - 600).status_code, 400)
            provider.assert_not_called()
        self.assertEqual(WebhookReceipt.objects.count(), 0)

    def test_flutterwave_verifies_transaction_again(self):
        p = self.payment('flutterwave')
        event = {'event': 'charge.completed', 'data': {'id': 22, 'tx_ref': str(p.id), 'status': 'successful'}}
        with patch('checkout.providers.flutterwave.verify', return_value='paid') as verify:
            self.assertEqual(self.send('flutterwave', event).status_code, 200)
            self.assertEqual(verify.call_args.args[1], '22')
        p.refresh_from_db()
        self.assertEqual(p.status, 'paid')

    def test_paypal_transmission_is_verified_before_capture(self):
        p = self.payment('paypal')
        event = {'id': 'WH-event', 'event_type': 'PAYMENT.CAPTURE.COMPLETED', 'resource': {
            'supplementary_data': {'related_ids': {'order_id': p.provider_id}},
        }}
        with patch('checkout.webhooks.paypal.headers', return_value={}), patch('checkout.webhooks.request', return_value={'verification_status': 'SUCCESS'}), patch('checkout.providers.paypal.verify', return_value='paid') as verify:
            self.assertEqual(self.send('paypal', event).status_code, 200)
            verify.assert_called_once()
        with patch('checkout.webhooks.paypal.headers', return_value={}), patch('checkout.webhooks.request', return_value={'verification_status': 'FAILURE'}):
            self.assertEqual(self.send('paypal', event).status_code, 400)

    def test_unknown_order_retries_and_unrelated_event_is_ignored(self):
        event = {'event': 'charge.success', 'data': {'id': 99, 'reference': str(uuid.uuid4())}}
        self.assertEqual(self.send('paystack', event).status_code, 503)
        self.assertEqual(self.send('paystack', {'event': 'subscription.create'}).status_code, 200)
        self.assertEqual(WebhookReceipt.objects.count(), 0)

    def test_malformed_bodies_do_not_crash(self):
        for raw in [b'[]', b'{', b'null', b'"text"']:
            self.assertEqual(self.client.post(f'{ROOT}/paystack', raw, content_type='application/json').status_code, 400)
        self.assertEqual(self.send('paystack', {'event': 'charge.success', 'data': []}).status_code, 400)

    @override_settings(PAYMENT_MODE='mock')
    def test_mock_mode_rejects_external_webhooks(self):
        self.assertEqual(self.send('paystack', {}).status_code, 404)
