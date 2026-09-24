from rest_framework import serializers

from .catalog import GATEWAYS, PRODUCTS
from .models import Payment


class CheckoutInput(serializers.Serializer):
    gateway = serializers.ChoiceField(choices=GATEWAYS)
    product = serializers.ChoiceField(choices=list(PRODUCTS))
    email = serializers.EmailField(max_length=254)

    def to_internal_value(self, data):
        # Reject client prices or misspelled fields instead of silently ignoring them.
        if not isinstance(data, dict) or set(data) - set(self.fields):
            raise serializers.ValidationError(
                {"non_field_errors": ["Send only gateway, product and email."]}
            )
        return super().to_internal_value(data)


class PaymentOutput(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "gateway",
            "mode",
            "product",
            "amount_minor",
            "currency",
            "status",
            "checkout_url",
            "created_at",
        ]
        read_only_fields = fields


class VerifyInput(serializers.Serializer):
    transaction_id = serializers.RegexField(r"^[0-9]{1,30}$", required=False)


class SimulationInput(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=["paid", "failed"])
