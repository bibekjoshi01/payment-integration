# Checkout architecture

## Find the code

- `dj_server/checkout/providers/` — one small adapter per gateway and shared HTTP/integrity helpers.
- `dj_server/checkout/services.py` — saved orders, idempotency and verification.
- `dj_server/checkout/webhooks.py` — provider authentication and duplicate handling.
- `dj_server/checkout/tests/` — checkout, adapter and webhook tests.
- `frontend/src/checkout/` — checkout form, result page, simulator and API client.
- [API examples](api.md) — requests you can run with curl.

The original auth, subscription and frontend prototypes remain in `dj_server/user`, `dj_server/subscription`, `frontend/src/components` and `frontend/src/pages` for reference. The new UI uses only `frontend/src/checkout`. Existing backend routes are retained for compatibility; use `/api/checkout/payments` for this example. The original tracked `db.sqlite3` is preserved; the running demo uses a new ignored `payment-demo.sqlite3`.

## How confirmation works

The backend chooses the price, saves a UUID reference, and creates hosted checkout. After return, it queries the provider and checks status, amount, currency and reference before marking the payment paid. PayPal also requires completed captures. Browser query parameters never establish payment success. A verified webhook calls the same verification service, so the browser does not have to return.

Repeated checkout requests must reuse their UUID `Idempotency-Key`. Different request data with the same key returns 409. The saved provider reference survives a network failure. Stripe and PayPal also receive upstream idempotency keys; Paystack and Flutterwave receive stable merchant references. Paid records never regress, and webhook receipts are recorded only after successful processing. Failed verification rolls back the receipt so the provider can retry.

## Before adapting to your application

This is a local guest-checkout teaching example, not a deployed store. Payment URLs act as unguessable bearer links; there is no customer ownership check. Add your application's authentication, authorization, rate limits, HTTPS, secret management and an order/fulfillment model before exposing it. Keep fulfillment transactional and idempotent. For traffic beyond local testing, use a database with row locks, queue webhook processing, and reconcile pending payments periodically; SQLite is intended for a single local developer here.

Demo USD and NGN prices are independent, not a currency conversion. Amount checks are exact: discounts, partial payments, refunds, disputes, tax and recurring billing are outside this checkout example. Provider sandboxes still require account access and supported payment methods. Automated tests use simulated upstream responses; run each guide's sandbox checks with your own credentials before integrating into a real system.

The original PayPal example contained embedded credentials. These have been removed from the working code; rotate them in PayPal if they were usable, since old Git history still contains them. Keep `.env` files out of Git.
