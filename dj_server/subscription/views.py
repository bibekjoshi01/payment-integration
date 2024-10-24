import stripe
from django.conf import settings
from rest_framework import status
from django.db import transaction
from rest_framework import generics
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializers import SubscribePlanSerializer, SubscriptionPlanSerializer
from .models import SubscriptionPlan, UserSubscription


class SubscribePlanAPIView(APIView):
    """
    Subscribe to a Plan
    """

    @transaction.atomic
    def post(self, request):
        serializer = SubscribePlanSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                instance = serializer.save()

                return Response(
                    {
                        "message": "Subscription created successfully.",
                        "session_id": instance.stripe_subscription_id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as err:
                return Response(
                    {"error": f"Subscription failed: {err}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveSessionView(APIView):
    def get(self, request, session_id):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            session = stripe.checkout.Session.retrieve(session_id)
            return Response(session, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanListAPIView(generics.ListAPIView):
    """API view to list subscription plans with their features"""

    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer



WEBHOOK_SECRET = "your_webhook_secret" 

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object'] 
        
        # Retrieve the user based on the session
        user_subscription = UserSubscription.objects.filter(
            stripe_subscription_id=session.get("id")
        ).first()
        
        if user_subscription:
            user_subscription.is_active = True 
            user_subscription.save()

    return JsonResponse({'status': 'success'}, status=200)
