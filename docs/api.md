# Checkout API

Base URL: `http://localhost:8000/api/checkout`. Use JSON. Routes have no trailing slash. These guest endpoints are for local learning; UUID payment links are bearer capabilities, not authenticated customer accounts.

## Configuration

```sh
curl http://localhost:8000/api/checkout/config
```

Returns the active `mode`, server catalog, supported gateway currencies and credential readiness. It never returns secrets. Readiness checks credential presence and test-key format, not whether a remote account will accept them.

## Create checkout

Generate a UUID (for example with `python3 -c 'import uuid; print(uuid.uuid4())'`), then:

```sh
curl -X POST http://localhost:8000/api/checkout/payments \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: 7f44987e-c319-466e-8d3f-b9ff219851f7' \
  -d '{"gateway":"paypal","product":"demo-guide","email":"buyer@example.com"}'
```

Use `paypal`, `stripe`, `paystack` or `flutterwave`. Send only the three documented fields. Amount and currency are selected by the server. The 201 response includes `id`, `gateway`, `mode`, `amount_minor`, `currency`, `status` and `checkout_url`. Navigate to `checkout_url` in a browser.

Retry the same body and key after a connection failure. It reuses the saved order; changed body or mode returns 409. Generate a new UUID for an intentional new purchase. Do not blindly create new payments after an uncertain provider response.

## Retrieve and verify

Replace `PAYMENT_ID` with the local UUID from the create response:

```sh
curl http://localhost:8000/api/checkout/payments/PAYMENT_ID
curl -X POST http://localhost:8000/api/checkout/payments/PAYMENT_ID/verify \
  -H 'Content-Type: application/json' -d '{}'
```

GET reads the saved state only. POST checks with the provider in sandbox mode. For Flutterwave, you may send `{"transaction_id":"12345"}` to additionally bind the returned transaction ID. A paid record is cached and cannot regress. `pending` means no confirmed payment, not success. In mock mode verification reads the simulated state without a provider call.

## Simulate a result

Available only for mock payments while the server is in mock mode:

```sh
curl -X POST http://localhost:8000/api/checkout/payments/PAYMENT_ID/simulate \
  -H 'Content-Type: application/json' -d '{"outcome":"paid"}'
```

Use `paid` or `failed`. Cancellation leaves the payment pending. The frontend's **New checkout** clears its saved request key. Do not use simulation as an actual fulfillment signal.

## Webhook URLs

Register `https://YOUR-BACKEND/api/checkout/webhooks/GATEWAY`, replacing `GATEWAY` with the provider name. Configure signatures as described in each provider guide. Webhooks are disabled in mock mode. Unsupported event types are acknowledged and ignored. Unknown local orders return 503 so a creation/delivery race can retry. A pending upstream result or upstream failure does not record a processed receipt.

## Errors

- 400: invalid request fields, malformed JSON or invalid webhook signature.
- 404: payment missing or simulation/webhook endpoint unavailable in this mode.
- 409: conflicting idempotency key, mode mismatch or concurrent checkout work.
- 502: provider error, timeout, invalid response or mismatched payment details.
- 503: missing test credentials, unknown webhook order or provider confirmation still pending.

Provider errors are deliberately generic; upstream bodies and credentials are not exposed. Use the provider's test dashboard to inspect a transaction by its saved reference.
