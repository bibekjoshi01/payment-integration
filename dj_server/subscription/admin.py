from django.contrib import admin

from .models import SubscriptionPlan, SubscriptionFeature, UserSubscription

admin.site.register(SubscriptionPlan)
admin.site.register(SubscriptionFeature)
admin.site.register(UserSubscription)
