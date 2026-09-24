"""Only server-owned prices are used to create provider checkouts (two-decimal currencies)."""

GATEWAYS = ("paypal", "stripe", "paystack", "flutterwave")
PRODUCTS = {
    "demo-guide": {
        "name": "Payment integration guide",
        "description": "A sample one-time purchase. No physical item is shipped.",
        "prices": {"USD": 1000, "NGN": 500000},
    },
}
CURRENCIES = {"paypal": "USD", "stripe": "USD", "paystack": "NGN", "flutterwave": "NGN"}
