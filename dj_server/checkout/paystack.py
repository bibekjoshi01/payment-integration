import requests
from django.conf import settings

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

        url = F"{PAYSTACK_BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": user_email,
            "amount": amount,  # Amount must be in kobo for NGN (e.g., 500 NGN = 50000 kobo)
            "callback_url": "http://localhost:5173/paystack-callback",
        }

        response = requests.post(url, json=data, headers=headers)
        res_data = response.json()

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
            return Response(
                {"message": "Payment successful", "data": res_data["data"]},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST
        )
