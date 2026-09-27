# Payment gateway examples

A React + Django checkout example for **PayPal, Stripe, Paystack and Flutterwave**. Start with a local simulator, then switch to actual provider sandboxes. This example covers one-time hosted payments; card details stay on provider pages.

## Run locally

Requires Python 3.12+ and Node.js 22.12+ (or 20.19+).

```sh
make setup
make backend
```

In a second terminal:

```sh
make frontend
```

Open **http://localhost:5173**. Pick a gateway, enter a test email, and choose success, failure or cancellation in the simulator. No API keys are needed. The UI labels simulated payments, and no money moves.

Without Make, follow [backend setup](dj_server/README.md) and [frontend setup](frontend/README.md).

## Try provider sandboxes

Copy `dj_server/.env.example` to `dj_server/.env`, set `PAYMENT_MODE=sandbox`, add the credentials for a gateway, and restart Django. Unconfigured gateways stay disabled. Backend dependency resolutions are pinned in `dj_server/requirements-lock.txt`. All credentials belong on the backend; the frontend needs no keys.

- [PayPal setup and test flow](docs/paypal.md) — sandbox buyer approval and Orders v2 capture.
- [Stripe setup and test flow](docs/stripe.md) — hosted Checkout and session retrieval.
- [Paystack setup and test flow](docs/paystack.md) — initialize and verify transactions in kobo.
- [Flutterwave setup and test flow](docs/flutterwave.md) — v3 Standard checkout and transaction verification.

Each guide links to the provider's actual API, webhook and testing documentation. Test-mode keys are required for Stripe, Paystack and Flutterwave. PayPal uses a fixed sandbox API host. There is no live mode.

## Tests

```sh
make test                 # Django checkout tests, no provider credentials or network
make frontend-check       # ESLint and production build
make browser-install      # One-time Chromium download
make browser-test         # Desktop + mobile against a real local mock backend
```

Browser tests start their own servers on ports 8000 and 5173; stop manually running servers first. They use `dj_server/browser-test.sqlite3`, separate from the local demo database. See [testing and troubleshooting](docs/testing.md).

## Find the code

- `dj_server/checkout/providers/` — one small adapter per gateway and shared HTTP/integrity helpers.
- `dj_server/checkout/services.py` — saved orders, idempotency and verification.
- `dj_server/checkout/webhooks.py` — provider authentication and duplicate handling.
- `dj_server/checkout/tests/` — checkout, adapter and webhook tests.
- `frontend/src/checkout/` — checkout form, result page, simulator and API client.
- [API examples](docs/api.md) — requests you can run with curl.

The original auth, subscription and frontend prototypes remain in `dj_server/user`, `dj_server/subscription`, `frontend/src/components` and `frontend/src/pages` for reference. The new UI uses only `frontend/src/checkout`. Existing backend routes are retained for compatibility; use `/api/checkout/payments` for this example. The original tracked `db.sqlite3` is preserved; the running demo uses a new ignored `payment-demo.sqlite3`.

## How confirmation works

The backend chooses the price, saves a UUID reference, and creates hosted checkout. After return, it queries the provider and checks status, amount, currency and reference before marking the payment paid. PayPal also requires completed captures. Browser query parameters never establish payment success. A verified webhook calls the same verification service, so the browser does not have to return.

Repeated checkout requests must reuse their UUID `Idempotency-Key`. Different request data with the same key returns 409. The saved provider reference survives a network failure. Stripe and PayPal also receive upstream idempotency keys; Paystack and Flutterwave receive stable merchant references. Paid records never regress, and webhook receipts are recorded only after successful processing. Failed verification rolls back the receipt so the provider can retry.

## Before adapting to your application

This is a local guest-checkout teaching example, not a deployed store. Payment URLs act as unguessable bearer links; there is no customer ownership check. Add your application's authentication, authorization, rate limits, HTTPS, secret management and an order/fulfillment model before exposing it. Keep fulfillment transactional and idempotent. For traffic beyond local testing, use a database with row locks, queue webhook processing, and reconcile pending payments periodically; SQLite is intended for a single local developer here.

Demo USD and NGN prices are independent, not a currency conversion. Amount checks are exact: discounts, partial payments, refunds, disputes, tax and recurring billing are outside this checkout example. Provider sandboxes still require account access and supported payment methods. Automated tests use simulated upstream responses; run each guide's sandbox checks with your own credentials before integrating into a real system.

The original PayPal example contained embedded credentials. These have been removed from the working code; rotate them in PayPal if they were usable, since old Git history still contains them. Keep `.env` files out of Git.
