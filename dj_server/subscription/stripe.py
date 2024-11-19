import logging
import stripe
from django.conf import settings

from rest_framework.exceptions import APIException

# Global logger setup for payment logs
payment_logger = logging.getLogger("payment_logger")
payment_logger.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# File handler for logging to a file
file_handler = logging.FileHandler("logs/payment_logs.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

# Add the handler to the logger
payment_logger.addHandler(file_handler)


def get_or_create_stripe_customer(user):
    """
    Check if the user has a Stripe customer ID.
    If not, create a new Stripe customer and store the customer ID.
    """
    
    try:
        if user.stripe_customer_id:
            # Try to retrieve the customer from Stripe
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            
            # Check if the customer has been deleted or not found
            if customer.get('deleted') or not customer:
                raise stripe.error.InvalidRequestError("Customer not found", "customer", None)
        
        else:
            # Create a new Stripe customer if not found or no customer ID
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name,
            )
            user.stripe_customer_id = customer["id"]
            user.save()

    except stripe.error.InvalidRequestError as e:
        # Customer not found or deleted in Stripe
        # Log the error, recreate the customer in Stripe
        payment_logger.error(f"Stripe error: {str(e)} - Creating new customer in Stripe")
        
        # Create new Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name,
        )
        user.stripe_customer_id = customer["id"]
        user.save()
    
    except stripe.error.StripeError as e:
        # Handle any Stripe errors
        raise APIException({f"Error creating Stripe customer: {e}"}, status=400)

    return user.stripe_customer_id


def create_stripe_checkout_session(user, subscription_plan):
    """Creates a Stripe Checkout session for the subscription"""
    
    # Set your Stripe secret key
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    stripe_customer_id = get_or_create_stripe_customer(user)

    if not subscription_plan.stripe_price_id:
        raise ValueError(
            "The subscription plan does not have a valid Stripe Price ID."
        )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            customer=stripe_customer_id,
            line_items=[
                {
                    "price": subscription_plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url="http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:5173/cancel",
        )
    except stripe.error.StripeError as e:
        raise APIException(
            {"error": "Failed to create subscription", "details": str(e)},
            status=400,
        )
        
    return session


def cancel_stripe_subscription(subscription_id):
        """
        Cancel a Stripe Subscription
        @see https://stripe.com/docs/api/subscriptions/cancel
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return {"message": "Subscription cancelled successfully."}, 204
        except stripe.error.StripeError as e:
            payment_logger.error(f"Stripe error: {e}")
            raise APIException(
                {"error": "Failed to cancel subscription", "details": str(e)},
                status=400,
            )


def get_subscription_status(subscription_id):
    """
    Retrieve the Stripe Subscription's status
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        return subscription.get("status"), 200
    except stripe.error.StripeError as e:
        payment_logger.error(f"Stripe error: {e}")
        raise APIException(
            {"error": "Failed to retrieve subscription", "details": str(e)},
            status=400,
        )



    