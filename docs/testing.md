# Testing and troubleshooting

## Local tests

```sh
make setup
make test
make frontend-check
make browser-install
make browser-test
```

Django tests use a disposable test database and stub upstream HTTP. They cover all gateways, request validation, idempotency conflicts, timeouts, amount/currency/reference mismatch, capture requirements, live-key rejection, signature rejection, stale Stripe signatures, duplicate events and webhook retries.

Playwright starts Django in mock mode and Vite, uses a separate `browser-test.sqlite3`, and runs success, failure and cancellation for every gateway on desktop and mobile. It also covers missing credentials, unknown payments and recovery from provider errors. It does not use actual cards or remote provider accounts. Stop your existing demo servers first; the tests deliberately do not attach to an unknown running server.

## Sandbox checks for each gateway

1. Follow the gateway's setup guide and confirm the UI says **Provider sandbox**.
2. Make a successful payment with provider test credentials/methods. Confirm the dashboard entry and local UUID reference, amount and currency.
3. Cancel or decline a payment. Confirm the app never reports it as paid.
4. Reload the result page and check status again. It should remain consistent.
5. Configure the signed webhook, start another checkout, and close the return tab. Use the saved payment URL or API to confirm the webhook updated it.
6. Use the provider dashboard to redeliver a matching event. It should be acknowledged without repeating a state change. An unrelated simulator event has no saved local order and will return 503.

These account-specific checks need your own sandbox credentials. Automated tests prove local behavior and mocked protocol handling; they do not prove that a particular merchant account is configured correctly.

## Common issues

**Cannot connect / blank response:** start Django on 8000 and Vite on 5173. The frontend's `/api` proxy handles both dev and preview. Navigate to `/api/checkout/config` to inspect the active mode.

**Gateway disabled:** check `dj_server/.env`, its test-key prefix and `PAYMENT_MODE=sandbox`, then restart Django. A configured label only checks format/presence; the provider can still reject expired or invalid credentials.

**No pending transaction found:** finish hosted checkout before verifying. Flutterwave may not have a transaction to retrieve before an attempt is made. A provider error leaves the saved state unchanged; retry rather than treating it as success.

**Idempotency conflict:** keep the original email/gateway/product for a retry, or use **New checkout** for a new order. Switching modes also requires a new order.

**Checkout creation failed after a timeout:** retry with the same key. PayPal/Stripe use provider idempotency; Paystack/Flutterwave use the same merchant reference. Some providers may reject an already initialized reference instead of returning the original checkout link. Check its dashboard and verify the saved order before intentionally starting a new one; this example cannot recover every provider session after an ambiguous timeout.

**Webhook never arrives:** localhost is not public. Use Stripe CLI for Stripe, or a public HTTPS tunnel for the other providers. Register the backend webhook URL, permit the tunnel hostname in `DJANGO_ALLOWED_HOSTS`, and use credentials for the same test account/app. Verify the secret/hash matches. Flutterwave here uses v3 `verif-hash`; Stripe uses snapshot Checkout events.

**Browser says cancelled but payment went through:** cancellation is a navigation event, not proof of failure. The result page still queries the provider, and a completed verified payment wins.

**SQLite busy / concurrent work:** retry with the same key. Run one local backend. For a real system, use PostgreSQL row locks, a webhook queue and periodic reconciliation instead of relying on a dev server and SQLite.

**Need a clean demo:** stop Django, remove `dj_server/payment-demo.sqlite3`, and run migrations again. This removes only local demo data. The preserved `db.sqlite3` is not used by this checkout.
