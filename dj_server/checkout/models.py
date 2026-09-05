import uuid

from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    idempotency_key = models.UUIDField(unique=True)
    gateway = models.CharField(max_length=20)
    mode = models.CharField(max_length=10)
    product = models.CharField(max_length=40)
    email = models.EmailField()
    amount_minor = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    provider_id = models.CharField(max_length=255, blank=True)
    checkout_url = models.URLField(max_length=2000, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WebhookReceipt(models.Model):
    gateway = models.CharField(max_length=20)
    event_id = models.CharField(max_length=255)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['gateway', 'event_id'], name='unique_gateway_event')]
