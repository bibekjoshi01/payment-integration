export const gateways = {
  paypal: { name: 'PayPal', mark: 'P', color: '#003087', detail: 'Sandbox buyer approval, followed by server capture.', docs: 'https://developer.paypal.com/docs/api/orders/v2/' },
  stripe: { name: 'Stripe', mark: 'S', color: '#635bff', detail: 'Hosted Checkout with a server-verified session.', docs: 'https://docs.stripe.com/payments/checkout' },
  paystack: { name: 'Paystack', mark: '≡', color: '#007a9b', detail: 'Hosted checkout with transaction reference verification.', docs: 'https://paystack.com/docs/payments/accept-payments/' },
  flutterwave: { name: 'Flutterwave', mark: 'F', color: '#b45c00', detail: 'Standard checkout with server-side transaction verification.', docs: 'https://developer.flutterwave.com/docs/flutterwave-standard-1' },
};
