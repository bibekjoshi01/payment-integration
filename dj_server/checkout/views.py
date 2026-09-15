from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .catalog import CURRENCIES, GATEWAYS, PRODUCTS
from .providers.common import NotConfigured, require
from .serializers import CheckoutInput, PaymentOutput, SimulationInput, VerifyInput
from .services import create_payment, find_payment, set_status, verify_payment


class PublicView(APIView):
    # These are guest checkout examples. Legacy API defaults remain unchanged.
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]


class ConfigView(PublicView):
    def get(self, request):
        gateways = []
        for gateway in GATEWAYS:
            ready = True
            if settings.PAYMENT_MODE == 'sandbox':
                try:
                    require(gateway)
                except NotConfigured:
                    ready = False
            gateways.append({'id': gateway, 'currency': CURRENCIES[gateway], 'ready': ready})
        return Response({'mode': settings.PAYMENT_MODE, 'products': PRODUCTS, 'gateways': gateways})


class PaymentCreateView(PublicView):
    def post(self, request):
        serializer = CheckoutInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = create_payment(serializer.validated_data, request.headers.get('Idempotency-Key'))
        return Response(PaymentOutput(payment).data, status=201)


class PaymentDetailView(PublicView):
    def get(self, request, payment_id):
        return Response(PaymentOutput(find_payment(payment_id)).data)


class PaymentVerifyView(PublicView):
    def post(self, request, payment_id):
        serializer = VerifyInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = verify_payment(find_payment(payment_id), serializer.validated_data.get('transaction_id'))
        return Response(PaymentOutput(payment).data)


class PaymentSimulateView(PublicView):
    def post(self, request, payment_id):
        payment = find_payment(payment_id)
        if settings.PAYMENT_MODE != 'mock' or payment.mode != 'mock':
            raise NotFound('Simulation is available only for mock payments in mock mode.')
        serializer = SimulationInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = set_status(payment, serializer.validated_data['outcome'])
        return Response(PaymentOutput(payment).data)
