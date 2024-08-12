import requests
from base64 import b64encode
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Constants
PAYPAL_CLIENT_ID="Ab5FpjAckC4yLes5rHjDIOxosZEbp6laV3DQukgYXRt_hyV4hbd-vXLsejnBtZvTlAsS2MJPsxz_OLlF"
PAYPAL_CLIENT_SECRET="EBGcjmS-HiULGQCsNEhyKLJUoVbTI_Dop5GWrFAzWOzSgH4DtpOHnB5Kg-DlrtGWvJadkM_HlvsbF080"
PAYPAL_BASE_URL = "https://api.sandbox.paypal.com"


class PaypalAPIView(APIView):
    permission_classes = [AllowAny]
    '''
    Generate an OAuth 2.0 access token for authenticating with PayPal REST APIs.
    @see https://developer.paypal.com/api/rest/authentication/
    '''
    def generate_access_token(self):
        try:
            if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
                raise ValueError("MISSING_API_CREDENTIALS")

            auth = b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode("utf-8")
            response = requests.post(f"{PAYPAL_BASE_URL}/v1/oauth2/token", data={
                "grant_type": "client_credentials",
            }, headers={
                "Authorization": f"Basic {auth}",
            })

            data = response.json()
            return data.get("access_token")
        except Exception as error:
            print("Failed to generate Access Token:", error)
            raise

    def handle_response(self, response):
        # Handle the response from paypal (Save necessary data in backend)
        # Pass the required response to frontend
        if response.status_code in [200, 201]:
            return response.json(), response.status_code
        else:
            return {"error": "Failed to create order."}, response.status_code


class CreateOrderView(PaypalAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):    
        try:
            cart = request.data.get("cart")
            jsonResponse, httpStatusCode = self.create_order(cart)
            return Response(jsonResponse, status=httpStatusCode)
        except Exception as error:
            print("Failed to create order:", error)
            return Response({"error": "Failed to create order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    Create an order to start the transaction.
    @see https://developer.paypal.com/docs/api/orders/v2/#orders_create
    '''
    def create_order(self, cart):
        # use the cart information passed from the front-end to calculate the purchase unit details
        print("shopping cart information passed from the frontend create_order() callback:", cart)

        # Validate the cart data in backend database 
        # Create order in backend and save information
        
        # Log the order information in paypal 
        access_token = self.generate_access_token()
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"
        payload = {
            # The merchant intends to capture payment immediately after the customer makes a payment.
            "intent": "CAPTURE", 
            # An array of purchase units. Each purchase unit establishes a contract between a payer and the payee. 
            "purchase_units": [
                {
                    "reference_id": 1,
                    "description": "The purchase description. ",
                    "invoice_id": "Appears in both the payer's transaction history and the emails that the payer receives.",
                    "amount": {
                        "currency_code": "USD",
                        "value": "100.00",
                    },
                },
            ],
        }

        response = requests.post(url, json=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        })

        return self.handle_response(response)


class CaptureOrderView(PaypalAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request, orderID):
        try:
            jsonResponse, httpStatusCode = self.capture_order(orderID)
            return Response(jsonResponse, status=httpStatusCode)
        except Exception as error:
            print("Failed to capture order:", error)
            return Response({"error": "Failed to capture order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    Capture payment for the created order to complete the transaction.
    @see https://developer.paypal.com/docs/api/orders/v2/#orders_capture
    '''
    def capture_order(self, orderID):
        access_token = self.generate_access_token()
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{orderID}/capture"

        response = requests.post(url, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            # Uncomment one of these to force an error for negative testing (in sandbox mode only). Documentation:
            # https://developer.paypal.com/tools/sandbox/negative-testing/request-headers/
            # "PayPal-Mock-Response": '{"mock_application_codes": "INSTRUMENT_DECLINED"}'
            # "PayPal-Mock-Response": '{"mock_application_codes": "TRANSACTION_REFUSED"}'
            # "PayPal-Mock-Response": '{"mock_application_codes": "INTERNAL_SERVER_ERROR"}'
        })

        return self.handle_response(response)