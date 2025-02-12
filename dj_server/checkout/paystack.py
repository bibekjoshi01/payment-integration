import requests
import json
import hashlib
import hmac

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"


class PayStackInitializePaymentView(APIView):
    """Initialize the payment"""

    permission_classes = [AllowAny]

    def post(self, request):
        # Use the data of payer user instead
        user_email = "test@gmail.com"  # Hard-Coded
        # Validate the amount
        amount = request.data.get("amount")  # Amount in kobo (subunit)

        if not user_email or not amount:
            return Response(
                {"error": "Email and amount are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": user_email,
            "amount": amount,  # Amount must be in kobo for NGN (e.g., 500 NGN = 50000 kobo)
            "callback_url": f"{settings.FRONTEND_BASE_URL}/paystack-callback",
        }

        response = requests.post(url, json=data, headers=headers)
        res_data = response.json()

        # Save the reference key
        # res_data.data.access_code

        if response.status_code == 200 and res_data.get("status"):
            return Response(res_data, status=status.HTTP_200_OK)

        return Response(
            {"error": "Failed to initialize payment"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PayStackVerifyPaymentView(APIView):
    """Verify Payment"""

    permission_classes = [AllowAny]

    def get(self, request, reference):
        # Validate the | reference | code with saved | access_code |

        url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)
        res_data = response.json()

        if (
            response.status_code == 200
            and res_data.get("status")
            and res_data["data"]["status"] == "success"
        ):
            # Save the transaction log as success
            return Response(
                {"message": "Payment successful", "data": res_data["data"]},
                status=status.HTTP_200_OK,
            )

        # Save the transaction log as failed
        return Response(
            {"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST
        )


class PayStackWebhook(APIView):
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def post(self, request):
        signature = request.headers.get("x-paystack-signature")
        payload = request.body

        # Validate signature
        computed_signature = hmac.new(
            key=PAYSTACK_SECRET_KEY.encode("utf-8"),
            msg=payload,
            digestmod=hashlib.sha512,
        ).hexdigest()

        if computed_signature != signature:
            return Response(
                {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Process the event
        event_type = event.get("event")
        data = event.get("data", {})

        # Get request_code or offline_reference
        request_code = data.get("request_code")
        offline_reference = data.get("offline_reference")

        if not request_code and not offline_reference:
            return Response(
                {"error": "Invalid transaction reference"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Validate the request code with access_code

        if event_type == "paymentrequest.success":
            # Handle successful charge
            print("Payment successful", data)
        else:
            print("Unhandled event", event_type)

        return Response({"status": "success"}, status=status.HTTP_200_OK)
