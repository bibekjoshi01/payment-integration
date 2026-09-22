import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from checkout.models import Payment
from checkout.providers.common import GatewayError
from checkout.services import set_status

ROOT = '/api/checkout'


@override_settings(PAYMENT_MODE='mock')
class CheckoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {'gateway': 'paypal', 'product': 'demo-guide', 'email': 'buyer@example.com'}
        self.key = str(uuid.uuid4())

    def create(self, **changes):
        return self.client.post(f'{ROOT}/payments', {**self.data, **changes}, format='json', HTTP_IDEMPOTENCY_KEY=self.key)

    def test_all_gateways_complete_locally_without_network(self):
        with patch('requests.request', side_effect=AssertionError('Unexpected network')):
            config = self.client.get(f'{ROOT}/config').json()
            self.assertEqual(config['mode'], 'mock')
            for gateway in ['paypal', 'stripe', 'paystack', 'flutterwave']:
                with self.subTest(gateway=gateway):
                    self.key = str(uuid.uuid4())
                    response = self.create(gateway=gateway)
                    self.assertEqual(response.status_code, 201)
                    payment = response.json()
                    self.assertNotIn('email', payment)
                    self.assertNotIn('provider_id', payment)
                    self.assertEqual(payment['currency'], 'USD' if gateway in ['paypal', 'stripe'] else 'NGN')
                    result = self.client.post(f"{ROOT}/payments/{payment['id']}/simulate", {'outcome': 'paid'}, format='json')
                    self.assertEqual(result.json()['status'], 'paid')
                    verified = self.client.post(f"{ROOT}/payments/{payment['id']}/verify", {}, format='json')
                    self.assertEqual(verified.json()['status'], 'paid')

    def test_idempotent_create_and_conflicting_body(self):
        first = self.create().json()
        self.assertEqual(self.create().json()['id'], first['id'])
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(self.create(email='other@example.com').status_code, 409)

    def test_requires_uuid_key_and_valid_input(self):
        self.key = 'invalid'
        self.assertEqual(self.create().status_code, 400)
        self.key = str(uuid.uuid4())
        for changes in [{'gateway': 'unknown'}, {'product': 'unknown'}, {'email': 'invalid'}, {'amount': 1}, {'currency': 'USD'}]:
            with self.subTest(changes=changes):
                self.assertEqual(self.create(**changes).status_code, 400)
        self.assertEqual(Payment.objects.count(), 0)

    def test_cancel_query_cannot_confirm_payment(self):
        payment = self.create().json()
        url = f"{ROOT}/payments/{payment['id']}"
        self.assertEqual(self.client.get(url + '?status=successful').json()['status'], 'pending')
        self.assertEqual(self.client.post(url + '/verify', {'status': 'successful'}, format='json').json()['status'], 'pending')

    def test_failure_and_monotonic_paid_state(self):
        payment = self.create().json()
        url = f"{ROOT}/payments/{payment['id']}/simulate"
        self.assertEqual(self.client.post(url, {'outcome': 'failed'}, format='json').json()['status'], 'failed')
        self.client.post(url, {'outcome': 'paid'}, format='json')
        stale = Payment.objects.get(pk=payment['id'])
        self.assertEqual(set_status(stale, 'pending').status, 'paid')
        self.assertEqual(self.client.post(url, {'outcome': 'failed'}, format='json').json()['status'], 'paid')

    def test_unknown_payment_returns_404(self):
        self.assertEqual(self.client.get(f'{ROOT}/payments/{uuid.uuid4()}').status_code, 404)
        self.assertEqual(self.client.get(f'{ROOT}/payments/not-a-uuid').status_code, 404)

    @override_settings(PAYMENT_MODE='sandbox', STRIPE_SECRET_KEY='')
    def test_missing_credentials_and_simulator_guard(self):
        self.assertEqual(self.create(gateway='stripe').status_code, 503)
        payment = Payment.objects.get()
        url = f'{ROOT}/payments/{payment.id}/simulate'
        self.assertEqual(self.client.post(url, {'outcome': 'paid'}, format='json').status_code, 404)
        self.assertEqual(payment.status, 'pending')

    def test_switching_modes_cannot_simulate_a_sandbox_payment(self):
        payment = self.create().json()
        Payment.objects.filter(pk=payment['id']).update(mode='sandbox')
        self.assertEqual(self.client.post(f"{ROOT}/payments/{payment['id']}/simulate", {'outcome': 'paid'}, format='json').status_code, 404)
        self.assertEqual(self.client.post(f"{ROOT}/payments/{payment['id']}/verify", {}, format='json').status_code, 409)

    @override_settings(PAYMENT_MODE='sandbox', STRIPE_SECRET_KEY='sk_test_example')
    def test_uncertain_provider_response_retains_reference_for_retry(self):
        with patch('checkout.providers.stripe.create', side_effect=GatewayError()):
            self.assertEqual(self.create(gateway='stripe').status_code, 502)
        saved = Payment.objects.get()
        with patch('checkout.providers.stripe.create', return_value=('cs_test_saved', 'https://checkout.stripe.com/test')) as create:
            self.assertEqual(self.create(gateway='stripe').json()['id'], str(saved.id))
            self.assertEqual(create.call_args.args[0].id, saved.id)
            self.create(gateway='stripe')
            self.assertEqual(create.call_count, 1)

    @override_settings(PAYMENT_MODE='sandbox', STRIPE_SECRET_KEY='sk_live_disallowed')
    def test_live_keys_not_accepted(self):
        self.assertEqual(self.create(gateway='stripe').status_code, 503)
