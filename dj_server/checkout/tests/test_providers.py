import copy
import uuid
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase, override_settings

from checkout.models import Payment
from checkout.providers import flutterwave, paypal, paystack, stripe
from checkout.providers.common import GatewayError, checkout_url, request


class ProviderTests(SimpleTestCase):
    def payment(self, gateway):
        return Payment(
            id=uuid.uuid4(),
            gateway=gateway,
            product="demo-guide",
            email="buyer@example.com",
            amount_minor=1000 if gateway in {"paypal", "stripe"} else 500000,
            currency="USD" if gateway in {"paypal", "stripe"} else "NGN",
            provider_id="provider-order",
            mode="sandbox",
        )

    def test_stripe_verification_rejects_wrong_reference_amount_currency_and_live_mode(
        self,
    ):
        p = self.payment("stripe")
        valid = {
            "id": p.provider_id,
            "mode": "payment",
            "livemode": False,
            "payment_status": "paid",
            "amount_total": 1000,
            "currency": "usd",
            "client_reference_id": str(p.id),
        }
        with patch.object(stripe, "request", return_value=valid):
            self.assertEqual(stripe.verify(p), "paid")
        for changes in [
            {"amount_total": 1},
            {"amount_total": "NaN"},
            {"currency": "ngn"},
            {"client_reference_id": str(uuid.uuid4())},
            {"livemode": True},
            {"id": "other"},
        ]:
            with (
                self.subTest(changes=changes),
                patch.object(stripe, "request", return_value={**valid, **changes}),
            ):
                with self.assertRaises(GatewayError):
                    stripe.verify(p)
        with patch.object(
            stripe, "request", return_value={**valid, "payment_status": "unpaid"}
        ):
            self.assertEqual(stripe.verify(p), "pending")

    def test_paystack_verifies_test_domain_and_amount_in_kobo(self):
        p = self.payment("paystack")
        data = {
            "domain": "test",
            "status": "success",
            "reference": str(p.id),
            "currency": "NGN",
            "amount": 500000,
        }
        for changes, valid in [
            ({}, True),
            ({"amount": 5000}, False),
            ({"domain": "live"}, False),
            ({"reference": "other"}, False),
            ({"currency": "USD"}, False),
        ]:
            with (
                self.subTest(changes=changes),
                patch.object(
                    paystack,
                    "request",
                    return_value={"status": True, "data": {**data, **changes}},
                ),
            ):
                if valid:
                    self.assertEqual(paystack.verify(p), "paid")
                else:
                    with self.assertRaises(GatewayError):
                        paystack.verify(p)

    def test_flutterwave_checks_reference_currency_amount_and_optional_transaction_id(
        self,
    ):
        p = self.payment("flutterwave")
        data = {
            "id": 123,
            "status": "successful",
            "tx_ref": str(p.id),
            "amount": "5000.00",
            "currency": "NGN",
        }
        with patch.object(
            flutterwave, "request", return_value={"status": "success", "data": data}
        ):
            self.assertEqual(flutterwave.verify(p, "123"), "paid")
            with self.assertRaises(GatewayError):
                flutterwave.verify(p, "456")
        for changes in [{"amount": 50}, {"currency": "USD"}, {"tx_ref": "other"}]:
            with (
                self.subTest(changes=changes),
                patch.object(
                    flutterwave,
                    "request",
                    return_value={"status": "success", "data": {**data, **changes}},
                ),
            ):
                with self.assertRaises(GatewayError):
                    flutterwave.verify(p)

    def test_paypal_captures_approved_orders_and_checks_completed_capture(self):
        p = self.payment("paypal")
        unit = {
            "custom_id": str(p.id),
            "amount": {"value": "10.00", "currency_code": "USD"},
        }
        approved = {"id": p.provider_id, "status": "APPROVED", "purchase_units": [unit]}
        completed = copy.deepcopy(approved)
        completed["status"] = "COMPLETED"
        completed["purchase_units"][0]["payments"] = {
            "captures": [
                {
                    "status": "COMPLETED",
                    "amount": {"value": "10.00", "currency_code": "USD"},
                }
            ]
        }
        with (
            patch.object(paypal, "headers", return_value={}),
            patch.object(
                paypal, "request", side_effect=[approved, {}, completed]
            ) as upstream,
        ):
            self.assertEqual(paypal.verify(p), "paid")
            self.assertEqual(upstream.call_args_list[1].args[0], "POST")
            self.assertIn("/capture", upstream.call_args_list[1].args[1])
            self.assertLessEqual(
                len(upstream.call_args_list[1].kwargs["headers"]["PayPal-Request-Id"]),
                38,
            )
        completed["purchase_units"][0]["payments"]["captures"][0]["amount"]["value"] = (
            "1.00"
        )
        with (
            patch.object(paypal, "headers", return_value={}),
            patch.object(paypal, "request", return_value=completed),
        ):
            with self.assertRaises(GatewayError):
                paypal.verify(p)
        approved["purchase_units"][0]["custom_id"] = "other"
        with (
            patch.object(paypal, "headers", return_value={}),
            patch.object(paypal, "request", return_value=approved) as upstream,
        ):
            with self.assertRaises(GatewayError):
                paypal.verify(p)
            self.assertEqual(
                upstream.call_count, 1, "Must reject another order before capture"
            )

    @override_settings(
        STRIPE_SECRET_KEY="sk_test_example",
        PAYSTACK_SECRET_KEY="sk_test_example",
        FLUTTERWAVE_SECRET_KEY="FLWSECK_TEST-example",
    )
    def test_checkout_payloads_use_server_prices_and_stable_references(self):
        p = self.payment("stripe")
        with patch.object(
            stripe,
            "request",
            return_value={"id": "session", "url": "https://checkout.stripe.com/test"},
        ) as upstream:
            stripe.create(p)
            self.assertEqual(
                upstream.call_args.kwargs["data"][
                    "line_items[0][price_data][unit_amount]"
                ],
                1000,
            )
            self.assertEqual(
                upstream.call_args.kwargs["headers"]["Idempotency-Key"], str(p.id)
            )
        p = self.payment("paystack")
        with patch.object(
            paystack,
            "request",
            return_value={
                "status": True,
                "data": {
                    "reference": str(p.id),
                    "authorization_url": "https://checkout.paystack.com/test",
                },
            },
        ) as upstream:
            paystack.create(p)
            self.assertEqual(upstream.call_args.kwargs["json"]["amount"], 500000)
            self.assertEqual(upstream.call_args.kwargs["json"]["reference"], str(p.id))
        p = self.payment("flutterwave")
        with patch.object(
            flutterwave,
            "request",
            return_value={
                "status": "success",
                "data": {"link": "https://checkout.flutterwave.com/test"},
            },
        ) as upstream:
            flutterwave.create(p)
            payload = upstream.call_args.kwargs["json"]
            self.assertEqual(payload["amount"], "5000.00")
            self.assertEqual(payload["tx_ref"], str(p.id))
            self.assertEqual(len(payload["payload_hash"]), 64)
        p = self.payment("paypal")
        with (
            patch.object(paypal, "headers", return_value={}),
            patch.object(
                paypal,
                "request",
                return_value={
                    "id": "order",
                    "links": [
                        {
                            "rel": "payer-action",
                            "href": "https://www.sandbox.paypal.com/test",
                        }
                    ],
                },
            ) as upstream,
        ):
            paypal.create(p)
            self.assertEqual(
                upstream.call_args.kwargs["json"]["purchase_units"][0]["amount"][
                    "value"
                ],
                "10.00",
            )

    def test_checkout_redirect_rejects_unsafe_destinations(self):
        for url in [
            "javascript:alert(1)",
            "http://checkout.stripe.com/x",
            "https://checkout.stripe.com.evil.test",
            "https://user@checkout.stripe.com/x",
        ]:
            with self.subTest(url=url), self.assertRaises(GatewayError):
                checkout_url(url, {"checkout.stripe.com"})

    @override_settings(PROVIDER_TIMEOUT=15)
    def test_network_failures_are_bounded_and_do_not_expose_upstream_bodies(self):
        for failure in [
            requests.Timeout("secret-token"),
            requests.HTTPError("secret-token"),
            ValueError("secret-token"),
        ]:
            with patch("requests.request", side_effect=failure) as upstream:
                with self.assertRaises(GatewayError) as caught:
                    request("GET", "https://provider.example")
                self.assertNotIn("secret-token", str(caught.exception))
                self.assertEqual(upstream.call_args.kwargs["timeout"], 15)
        response = Mock()
        response.json.return_value = ["unexpected"]
        with (
            patch("requests.request", return_value=response),
            self.assertRaises(GatewayError),
        ):
            request("GET", "https://provider.example")
