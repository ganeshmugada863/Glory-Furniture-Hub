from django.db import models
from django.contrib.auth.models import User
import uuid

class Booking(models.Model):
    CONSULTATION_TYPES = [
        ('Showroom Visit', 'Showroom Visit (Banjara Hills / Kukatpally)'),
        ('Video Consultation', 'Live Video Design Consultation'),
        ('In-Home Site Measurement', 'Master Artisan In-Home Measurement'),
        ('Product Order & In-Home Delivery', 'Product Order & In-Home Delivery'),
    ]

    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Scheduled', 'Scheduled'),
        ('In Review', 'In Review'),
        ('Payment Pending', 'Payment Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    booking_id = models.CharField(max_length=50, unique=True, blank=True)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    consultation_type = models.CharField(max_length=80, choices=CONSULTATION_TYPES, default='Showroom Visit')
    preferred_date = models.DateField()
    time_slot = models.CharField(max_length=80, default='10:00 AM - 11:30 AM')
    wood_preference = models.CharField(max_length=120, default='Pure Grade-A Burma Teak')
    address = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"GLORY-BK-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.customer_name} ({self.status})"


class Order(models.Model):
    PLAN_CHOICES = [
        ('FULL_PAYMENT', 'Full Payment'),
        ('THREE_INSTALLMENTS', 'Three Installments'),
    ]

    STATUS_CHOICES = [
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('FULLY_PAID', 'Fully Paid'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # Customer Details
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    shipping_address = models.TextField(blank=True, default='')

    # Product Details
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE, related_name='orders')
    product_name = models.CharField(max_length=250)
    selected_size = models.CharField(max_length=100, default='Standard')
    selected_wood = models.CharField(max_length=120, default='Pure Grade-A Burma Teak')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Financial breakdown (in Indian Rupees with 2 decimal precision; internally calculated in paise)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_plan = models.CharField(max_length=30, choices=PLAN_CHOICES, default='FULL_PAYMENT')
    order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING_PAYMENT')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        if self.remaining_amount is None:
            self.remaining_amount = self.total_amount - (self.paid_amount or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} (₹{self.total_amount})"

    @property
    def formatted_total(self):
        return f"₹{int(self.total_amount):,}"

    @property
    def formatted_paid(self):
        return f"₹{int(self.paid_amount):,}"

    @property
    def formatted_remaining(self):
        return f"₹{int(self.remaining_amount):,}"

    @property
    def payment_status(self):
        return self.order_status

    @property
    def next_due_installment(self):
        return self.installments.filter(status__in=['PENDING', 'OVERDUE']).order_by('installment_number').first()

    def update_financial_status(self):
        """Recalculate paid and remaining amounts from successful transactions/paid installments."""
        from decimal import Decimal
        if self.payment_plan == 'THREE_INSTALLMENTS' and self.installments.exists():
            paid_sum = sum((inst.amount for inst in self.installments.filter(status='PAID')), Decimal('0.00'))
        else:
            paid_sum = sum((t.amount for t in self.transactions.filter(status='SUCCESS')), Decimal('0.00'))

        self.paid_amount = paid_sum
        self.remaining_amount = max(Decimal('0.00'), self.total_amount - paid_sum)
        if self.paid_amount == Decimal('0.00'):
            self.order_status = 'PENDING_PAYMENT'
        elif self.paid_amount >= self.total_amount:
            self.order_status = 'FULLY_PAID'
        else:
            self.order_status = 'PARTIALLY_PAID'
        self.save()


class Installment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    payment_id = models.CharField(max_length=100, blank=True, default='')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['installment_number']
        unique_together = ('order', 'installment_number')

    def __str__(self):
        return f"{self.order.order_number} - Installment {self.installment_number} (₹{self.amount}) [{self.status}]"

    @property
    def transaction_reference(self):
        return self.payment_id

    @property
    def gateway_payment_id(self):
        return self.payment_id

    @property
    def formatted_amount(self):
        return f"₹{int(self.amount):,}"

    @property
    def is_eligible_for_payment(self):
        """Can be paid if PENDING or OVERDUE, and all previous installments are PAID."""
        if self.status not in ['PENDING', 'OVERDUE']:
            return False
        if self.installment_number == 1:
            return True
        previous_unpaid = Installment.objects.filter(
            order=self.order,
            installment_number__lt=self.installment_number
        ).exclude(status='PAID').exists()
        return not previous_unpaid

    @property
    def is_eligible_for_reschedule(self):
        """Admins can reschedule PENDING, OVERDUE, or FAILED installments, but not PAID ones."""
        return self.status in ['PENDING', 'OVERDUE', 'FAILED']


class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    installment = models.ForeignKey(Installment, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    gateway = models.CharField(max_length=50, default='Razorpay')
    gateway_payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    gateway_order_id = models.CharField(max_length=100, blank=True, default='')
    gateway_signature = models.CharField(max_length=255, blank=True, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='INITIATED')
    failure_reason = models.TextField(blank=True, default='')
    idempotency_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"TXN {self.gateway_payment_id or self.id} - ₹{self.amount} ({self.status})"


class InstallmentRescheduleAudit(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reschedule_audits')
    installment = models.ForeignKey(Installment, on_delete=models.CASCADE, related_name='reschedule_audits')
    old_due_date = models.DateField()
    new_due_date = models.DateField()
    changed_by = models.CharField(max_length=150, default='Master Studio Admin')
    reason = models.TextField()
    customer_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Audit {self.order.order_number} Inst {self.installment.installment_number}: {self.old_due_date} -> {self.new_due_date}"

