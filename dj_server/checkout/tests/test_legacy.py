from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from subscription.views import stripe_webhook


class LegacyWebhookTests(SimpleTestCase):
    def request(self):
        request = APIRequestFactory().post(
            "/legacy-webhook",
            b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid",
        )
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True))
        return request

    @override_settings(STRIPE_WEBHOOK_SECRET="")
    def test_missing_secret_fails_closed(self):
        self.assertEqual(stripe_webhook(self.request()).status_code, 503)

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_example")
    def test_invalid_signature_is_rejected(self):
        self.assertEqual(stripe_webhook(self.request()).status_code, 400)
