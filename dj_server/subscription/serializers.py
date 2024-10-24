from dateutil.relativedelta import relativedelta
from rest_framework import serializers

from .stripe import create_stripe_checkout_session
from .constants import SUBSCRIPTION_PLAN_DURATION
from .models import SubscriptionPlan, UserSubscription
from django.utils import timezone
from .models import SubscriptionPlan, SubscriptionFeature


class SubscribePlanSerializer(serializers.ModelSerializer):
    """Serializer to handle subscription for a user"""

    subscription_plan = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all()
    )

    class Meta:
        model = UserSubscription
        fields = ["user", "subscription_plan"]

    def create(self, validated_data):
        user = validated_data["user"]
        subscription_plan = validated_data["subscription_plan"]

        # Create Stripe checkout session
        stripe_session = create_stripe_checkout_session(user, subscription_plan)

        start_date = timezone.now()
        end_date = start_date + relativedelta(months=SUBSCRIPTION_PLAN_DURATION)

        # Save the subscription in the database
        user_subscription = UserSubscription.objects.create(
            user=user,
            subscription_plan=subscription_plan,
            stripe_subscription_id=stripe_session["id"],
            start_date=start_date,
            end_date=end_date,
            is_active=False,
        )

        return user_subscription


class SubscriptionFeatureSerializer(serializers.ModelSerializer):
    """Serializer for Subscription Plan Features"""

    class Meta:
        model = SubscriptionFeature
        fields = ["id", "feature_name"]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for Subscription Plans with Features"""

    features = SubscriptionFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "description", "price", "features"]


