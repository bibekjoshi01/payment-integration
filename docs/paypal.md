# PayPal sandbox

1. Create a **sandbox REST app** in the [PayPal developer dashboard](https://developer.paypal.com/dashboard/applications/sandbox).
2. Put its client ID and secret in `dj_server/.env` as `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET`. Set `PAYMENT_MODE=sandbox` and restart Django.
3. Choose PayPal in the playground. The backend obtains an OAuth token, creates an order with the saved USD amount and local UUID, and returns the approval link.
4. Sign in with a sandbox **personal buyer account**, not the merchant account. Approve and return to the app. The backend retrieves the order, captures an approved order, then checks the completed capture amount, currency and order reference.
5. Try cancelling approval too. Cancellation does not confirm payment; use **Resume checkout** or start a new order.

The API host is fixed to `api-m.sandbox.paypal.com`. Live credentials do not switch this example to production. A browser `token` is not trusted to select the order to capture: the backend uses its saved provider order ID. Create and capture use separate stable `PayPal-Request-Id` values.

## Webhooks

Register a publicly reachable HTTPS URL ending in `/api/checkout/webhooks/paypal` on the **same sandbox app**. Subscribe to `CHECKOUT.ORDER.APPROVED` and `PAYMENT.CAPTURE.COMPLETED`. Set `PAYPAL_WEBHOOK_ID` to the resulting webhook ID, add the tunnel hostname to `DJANGO_ALLOWED_HOSTS`, and restart Django.

PayPal transmission headers and the event are sent to PayPal's signature verification endpoint. Only verified events can trigger order retrieval/capture. Webhook delivery can confirm payment after the buyer closes the browser. Unrelated webhook simulator events may not match a saved order; a real checkout made through this app is the end-to-end test.

## Official documentation

- [REST authentication](https://developer.paypal.com/api/rest/authentication/)
- [Orders v2: create, retrieve, capture](https://developer.paypal.com/docs/api/orders/v2/)
- [Idempotency](https://developer.paypal.com/api/rest/reference/idempotency/)
- [Webhook signature verification](https://developer.paypal.com/docs/api/webhooks/v1/#verify-webhook-signature_post)
- [Sandbox accounts](https://developer.paypal.com/tools/sandbox/accounts/)

Implementation: [`providers/paypal.py`](../dj_server/checkout/providers/paypal.py).
