from django.db import models
from django.conf import settings
from .base import AbstractInfoModel
from django.utils.translation import gettext_lazy as _


class SubscriptionPlan(AbstractInfoModel):
    """Subscription Plan Model"""

    name = models.CharField(_("Plan Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(
        max_length=255, blank=True, help_text="Stripe price ID"
    )

    class Meta:
        verbose_name = _("Subscription Plan")
        verbose_name_plural = _("Subscription Plans")

    def __str__(self):
        return self.name


class SubscriptionFeature(models.Model):
    """Subscription Plan Feature Model"""

    subscription_plan = models.ForeignKey(
        SubscriptionPlan, related_name="features", on_delete=models.CASCADE
    )
    feature_name = models.CharField(_("Feature Name"), max_length=255)

    def __str__(self):
        return f"{self.feature_name} ({self.subscription_plan.name})"


class UserSubscription(models.Model):
    """User Subscription Model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    stripe_subscription_id = models.CharField(
        max_length=255, blank=True, help_text="Stripe Subscription ID"
    )
    start_date = models.DateTimeField(_("Start Date"))
    end_date = models.DateTimeField(_("End Date"))
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_plan.name}"
