# Stripe Checkout

1. Open a [Stripe sandbox or test environment](https://docs.stripe.com/sandboxes), and copy its secret key into `STRIPE_SECRET_KEY` in `dj_server/.env`.
2. Set `PAYMENT_MODE=sandbox` and restart Django. The key must start with `sk_test_`; live keys are rejected.
3. Choose Stripe and continue to hosted Checkout. The backend creates a one-time card session with inline price data, the saved USD amount and order UUID. No Dashboard product setup or frontend publishable key is required.
4. Complete checkout using a card from [Stripe's testing documentation](https://docs.stripe.com/testing), with a future expiry. Try a declined test card and the browser Back/cancel flow as well.
5. The return page retrieves the saved session on the backend. Only a test-mode session with matching reference, total, currency and `payment_status=paid` can confirm the order.

## Webhooks locally

Install the [Stripe CLI](https://docs.stripe.com/stripe-cli), then run:

```sh
stripe login
stripe listen --events checkout.session.completed,checkout.session.async_payment_succeeded,checkout.session.async_payment_failed,checkout.session.expired --forward-to http://localhost:8000/api/checkout/webhooks/stripe
```

Copy the printed signing secret into `STRIPE_WEBHOOK_SECRET`, restart Django, and complete another checkout. The CLI listener secret is different from a Dashboard endpoint secret. Use snapshot Checkout events for this example. Dashboard webhook URLs must use public HTTPS.

The handler validates the raw-body signature with Stripe's SDK, including its timestamp tolerance. It then retrieves the saved session instead of trusting the event's payment fields. An unrelated `stripe trigger` fixture has no saved payment here; use the app's checkout to test a matching order.

## Official documentation

- [Hosted Checkout](https://docs.stripe.com/payments/checkout)
- [Create a Checkout Session](https://docs.stripe.com/api/checkout/sessions/create)
- [Fulfill orders](https://docs.stripe.com/checkout/fulfillment)
- [Receive webhooks](https://docs.stripe.com/webhooks)
- [Idempotent requests](https://docs.stripe.com/api/idempotent_requests)

Implementation: [`providers/stripe.py`](../dj_server/checkout/providers/stripe.py).
