import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class InstallmentPlan(models.Model):
    """
    Admin-configurable global installment plan.
    Orders store a snapshot of their plan so modifications to global plans
    never alter existing customer contracts.
    """
    name = models.CharField(max_length=100, help_text="e.g. 2 Installments, 3 Monthly Payments, 6 Installments")
    slug = models.SlugField(max_length=100, unique=True)
    installment_count = models.PositiveSmallIntegerField(default=3, help_text="Number of payments")
    percentages = models.JSONField(
        default=list,
        help_text="Optional percentage distribution e.g. [33.33, 33.33, 33.34]. If empty, split equally."
    )
    interval_days = models.PositiveIntegerField(default=30, help_text="Days between each installment")
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), help_text="Minimum order total required")
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Maximum order total allowed")
    is_active = models.BooleanField(default=True, help_text="Only active plans are displayed during checkout")
    description = models.TextField(blank=True, default='', help_text="Short patron-facing explanation")
    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'installment_count']
        verbose_name = 'Installment Plan'
        verbose_name_plural = 'Installment Plans'

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.name} ({self.installment_count} parts) [{status}]"


class Payment(models.Model):
    """
    Unified transaction ledger tracking all Cashfree payments,
    supporting both Full Payment and individual Installments.
    """
    PAYMENT_TYPE_CHOICES = [
        ('FULL', 'Full Payment'),
        ('INSTALLMENT', 'Installment Payment'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    payment_id = models.CharField(max_length=100, unique=True, blank=True, db_index=True)
    order = models.ForeignKey('bookings.Order', on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    installment = models.ForeignKey('bookings.Installment', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='FULL')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')

    # Gateway Details
    gateway = models.CharField(max_length=50, default='Cashfree')
    gateway_order_id = models.CharField(max_length=120, blank=True, default='', db_index=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True, default='', db_index=True)
    payment_session_id = models.CharField(max_length=255, blank=True, default='')
    payment_method = models.CharField(max_length=50, blank=True, default='UPI')

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True, default='')

    # Refund management
    refund_status = models.CharField(max_length=30, blank=True, default='')
    refund_id = models.CharField(max_length=100, blank=True, default='')

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'

    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"GLORY-PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id} | ₹{self.amount} | {self.payment_type} ({self.status})"

    @property
    def formatted_amount(self):
        return f"₹{int(self.amount):,}"


class WebhookEvent(models.Model):
    """
    Idempotent ledger of all webhook notifications received from Cashfree.
    Prevents duplicate processing and race conditions.
    """
    STATUS_CHOICES = [
        ('RECEIVED', 'Received'),
        ('PROCESSED', 'Processed'),
        ('IGNORED', 'Ignored'),
        ('FAILED', 'Failed'),
    ]

    event_id = models.CharField(max_length=120, blank=True, default='', db_index=True)
    event_type = models.CharField(max_length=100, blank=True, default='')
    gateway_order_id = models.CharField(max_length=120, blank=True, default='', db_index=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True, default='')
    payload_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 hash of payload")
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='RECEIVED')
    error_message = models.TextField(blank=True, default='')
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Cashfree Webhook Event'
        verbose_name_plural = 'Cashfree Webhook Events'

    def __str__(self):
        return f"Webhook [{self.event_type}] {self.gateway_order_id} - {self.status}"
