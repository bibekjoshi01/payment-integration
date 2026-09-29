# Paystack test checkout

1. Get a **test** secret key from the [Paystack dashboard](https://dashboard.paystack.com/). Put it in `PAYSTACK_SECRET_KEY` in `dj_server/.env`.
2. Set `PAYMENT_MODE=sandbox` and restart Django. Keys must start with `sk_test_`.
3. Select Paystack, enter a test email, and continue to hosted checkout. The backend sends the saved reference and **500000 kobo = NGN 5000**. The browser cannot set the amount.
4. Use the test payment methods from [Paystack's test payments guide](https://paystack.com/docs/payments/test-payments/). Try a successful payment, a failed payment and abandoning checkout.
5. On return, the backend verifies the saved reference. It requires the `test` domain, `success` transaction status, expected kobo amount and NGN currency. The API response's top-level `status` alone does not mean the payment succeeded.

## Webhooks

In the Dashboard's test integration settings, register a public HTTPS URL ending in `/api/checkout/webhooks/paystack`. Add the tunnel hostname to `DJANGO_ALLOWED_HOSTS` and restart Django. There is no separate webhook secret: Paystack signs the raw body with the test secret key in `x-paystack-signature` (HMAC SHA512).

This example handles `charge.success`, then re-queries the transaction. Duplicate event deliveries do not repeat confirmation. The signed transaction must belong to a saved local Paystack payment; an unrelated Dashboard test event is not enough.

Paystack uses the same API host for test and live keys, so both key checks and the verified transaction's domain protect this example's sandbox boundary. Use a fresh order after an expired or abandoned checkout; keep the same idempotency key when retrying a network error for the same order.

## Official documentation

- [Accept payments](https://paystack.com/docs/payments/accept-payments/)
- [Initialize and verify transactions](https://paystack.com/docs/api/transaction/)
- [Verify payments](https://paystack.com/docs/payments/verify-payments/)
- [Webhook signatures and retries](https://paystack.com/docs/payments/webhooks/)
- [Test payments](https://paystack.com/docs/payments/test-payments/)

Implementation: [`providers/paystack.py`](../dj_server/checkout/providers/paystack.py).
