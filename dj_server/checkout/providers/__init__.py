from . import flutterwave, paypal, paystack, stripe
from .common import require

PROVIDERS = {
    "paypal": paypal,
    "stripe": stripe,
    "paystack": paystack,
    "flutterwave": flutterwave,
}


def get_provider(gateway):
    require(gateway)
    return PROVIDERS[gateway]
