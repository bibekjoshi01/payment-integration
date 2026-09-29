# Flutterwave v3 Standard

1. Use a Flutterwave account with access to **v3 test API keys**. Get the test secret from the [dashboard](https://dashboard.flutterwave.com/) and set `FLUTTERWAVE_SECRET_KEY` in `dj_server/.env`.
2. Set `PAYMENT_MODE=sandbox` and restart Django. Keys must start with `FLWSECK_TEST-`. This adapter uses v3 Standard and does not use v4 OAuth credentials.
3. Choose Flutterwave and continue to hosted checkout. The backend sends a stable `tx_ref`, **NGN 5000.00**, the email and return URL. It also generates a server-side payload checksum from saved values.
4. Use methods from [Flutterwave's test helpers](https://developer.flutterwave.com/docs/testing). Complete a test payment and return. Also try failure or cancellation.
5. The backend verifies by the saved `tx_ref`; it requires `successful`, the exact NGN amount, currency and reference. If the return includes `transaction_id`, it must match too. Browser `status=successful` is never sufficient.

Use `http://localhost:5173` in the browser, rather than its IP address, as required by Flutterwave checkout testing. NGN is used for this example. Availability of test payment methods depends on your account and dashboard settings. A transaction that does not yet exist at the provider may return a verification error; leave it unconfirmed and retry the status check after completing checkout.

## Webhooks

Set a random secret hash in the Dashboard's v3 webhook settings and copy it to `FLUTTERWAVE_WEBHOOK_SECRET`. Register a public HTTPS URL ending in `/api/checkout/webhooks/flutterwave`. Add the tunnel hostname to `DJANGO_ALLOWED_HOSTS` and restart Django.

This adapter follows the v3 `verif-hash` webhook scheme and handles `charge.completed`. The secret header is checked before re-querying the saved transaction. It does not accept an unsigned event, and a failed event cannot undo a paid order. Configure webhook retries in your dashboard. Accounts using a different API generation or signature scheme need a matching adapter; do not disable verification to make an event pass.

## Official documentation

- [Flutterwave Standard](https://developer.flutterwave.com/docs/flutterwave-standard-1)
- [Transaction verification](https://developer.flutterwave.com/docs/transaction-verification)
- [Verify by merchant reference](https://developer.flutterwave.com/reference/verify-transaction-with-tx_ref)
- [Payload checksum](https://developer.flutterwave.com/docs/checksum)
- [v3 webhook verification](https://developer.flutterwave.com/v3.0.0/docs/webhooks)
- [Test helpers](https://developer.flutterwave.com/docs/testing)

Implementation: [`providers/flutterwave.py`](../dj_server/checkout/providers/flutterwave.py).
