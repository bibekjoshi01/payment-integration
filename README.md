# Payment gateway examples

React + Django examples for **PayPal, Stripe, Paystack and Flutterwave**. Try one-time payments with a local simulator or provider sandbox. Live payments are disabled.

## Run

Requires Python 3.12+ and Node.js 22.12+ (or 20.19+).

```sh
make setup
make backend
```

In a second terminal:

```sh
make frontend
```

Open **http://localhost:5173**. Select a gateway, enter a test email, and simulate success, failure or cancellation. No API keys are needed.

For setup without Make, see the [backend](dj_server/README.md) and [frontend](frontend/README.md) instructions.

## Test

```sh
make test              # Backend tests
make frontend-check    # Lint and build
make browser-install   # Download Chromium once
make browser-test      # Desktop and mobile tests
```

Stop running servers on ports 8000 and 5173 before browser tests; they start their own servers.

## Provider sandboxes

Copy `dj_server/.env.example` to `dj_server/.env`, set `PAYMENT_MODE=sandbox`, add provider test credentials, and restart Django. Keep secrets on the backend.

Setup and official documentation: [PayPal](docs/paypal.md), [Stripe](docs/stripe.md), [Paystack](docs/paystack.md), [Flutterwave](docs/flutterwave.md).

More details: [API examples](docs/api.md), [testing and troubleshooting](docs/testing.md), [architecture](docs/architecture.md).
