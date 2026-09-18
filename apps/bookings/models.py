from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
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

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('FULLY_PAID', 'Fully Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    FULFILLMENT_STATUS_CHOICES = [
        ('CONFIRMED', 'CONFIRMED'),
        ('IN_PRODUCTION', 'IN_PRODUCTION'),
        ('SHIPPED', 'SHIPPED'),
        ('OUT_FOR_DELIVERY', 'OUT_FOR_DELIVERY'),
        ('DELIVERED', 'DELIVERED'),
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
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    payment_plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='FULL_PAYMENT')
    payment_type = models.CharField(max_length=20, choices=[('FULL', 'Full Payment'), ('INSTALLMENT', 'Installment Payment')], default='FULL')
    plan_name = models.CharField(max_length=120, default='Full Payment', blank=True)
    installment_plan_snapshot = models.JSONField(default=dict, blank=True, help_text="Snapshot of the chosen installment plan schedule")
    next_due_date = models.DateField(null=True, blank=True)

    # Core Decoupled Statuses
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='PENDING', db_index=True)
    fulfillment_status = models.CharField(max_length=30, choices=FULFILLMENT_STATUS_CHOICES, default='CONFIRMED', db_index=True)

    # Legacy field kept strictly for historical backward compatibility. Do not sync payment/fulfillment into it.
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
    def next_due_installment(self):
        return self.installments.filter(status__in=['PENDING', 'OVERDUE']).order_by('installment_number').first()

    @property
    def delivery_address_display(self):
        """Returns clean formatted delivery address falling back to booking or profile address."""
        if self.shipping_address and self.shipping_address.strip():
            return self.shipping_address.strip()
        try:
            if self.booking and self.booking.address and self.booking.address.strip():
                return self.booking.address.strip()
        except Exception:
            pass
        try:
            if self.user and hasattr(self.user, 'profile') and self.user.profile.address and self.user.profile.address.strip():
                return self.user.profile.address.strip()
        except Exception:
            pass
        return "Plot 42, Jubilee Hills Road No. 36, Hyderabad, Telangana 500033"

    def get_flipkart_timeline(self):
        """
        Constructs a structured 5-stage Flipkart-style order tracking timeline:
        1. CONFIRMED (Order Confirmed)
        2. IN_PRODUCTION (In Production)
        3. SHIPPED (Shipped)
        4. OUT_FOR_DELIVERY (Out for Delivery)
        5. DELIVERED (Delivered)
        Returns stage metadata with timestamps, completion flags, and artisan notes.
        """
        from datetime import timedelta
        stage_order = ['CONFIRMED', 'IN_PRODUCTION', 'SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']
        current_status = self.fulfillment_status
        current_idx = stage_order.index(current_status) if current_status in stage_order else 0

        # Build map of stage history entries
        histories = list(self.status_history.all().order_by('created_at'))
        history_by_status = {}
        for h in histories:
            history_by_status[h.fulfillment_status] = h

        stages_meta = [
            {
                'key': 'CONFIRMED',
                'title': 'CONFIRMED',
                'subtitle': 'Your order has been placed & timber seasoned.',
                'icon': '✓',
                'default_note': 'Order verified and requisitioned at Hyderabad Central Workshop.',
            },
            {
                'key': 'IN_PRODUCTION',
                'title': 'IN_PRODUCTION',
                'subtitle': 'Master carpentry, joinery & fine buffing.',
                'icon': '🔨',
                'default_note': 'Artisan mortise-and-tenon joinery and carving in progress.',
            },
            {
                'key': 'SHIPPED',
                'title': 'SHIPPED',
                'subtitle': 'Dispatched with protective white-glove packaging.',
                'icon': '🚛',
                'default_note': 'Dispatched from central Hyderabad workshop via specialized furniture transport.',
            },
            {
                'key': 'OUT_FOR_DELIVERY',
                'title': 'OUT_FOR_DELIVERY',
                'subtitle': 'Local white-glove transport team assigned.',
                'icon': '📦',
                'default_note': 'Artisan delivery team is en route with in-home placement service.',
            },
            {
                'key': 'DELIVERED',
                'title': 'DELIVERED',
                'subtitle': 'Piece delivered, assembled & warranty activated.',
                'icon': '🏠',
                'default_note': 'Delivered and assembled with 10-year teak warranty certificate.',
            },
        ]

        timeline = []
        for idx, meta in enumerate(stages_meta):
            key = meta['key']
            is_completed = (idx <= current_idx)
            is_current = (idx == current_idx)
            is_upcoming = (idx > current_idx)

            hist_entry = history_by_status.get(key)
            if key == 'CONFIRMED':
                timestamp = self.created_at
                notes = hist_entry.admin_notes if hist_entry and hist_entry.admin_notes else meta['default_note']
            elif hist_entry:
                timestamp = hist_entry.created_at
                notes = hist_entry.admin_notes if hist_entry.admin_notes else meta['default_note']
            elif is_completed:
                timestamp = self.updated_at
                notes = meta['default_note']
            else:
                projected_days = (idx * 3)
                timestamp = (self.created_at + timedelta(days=projected_days)) if self.created_at else None
                notes = meta['default_note']

            timeline.append({
                'key': key,
                'stage_number': idx + 1,
                'title': meta['title'],
                'subtitle': meta['subtitle'],
                'icon': meta['icon'],
                'is_completed': is_completed,
                'is_current': is_current,
                'is_upcoming': is_upcoming,
                'timestamp': timestamp,
                'notes': notes,
                'has_admin_note': bool(hist_entry and hist_entry.admin_notes),
            })

        return timeline

    def recalculate_financials(self):
        """
        Calculates verified paid amounts, remaining balances, and financial payment status.
        Enforces:
        1. Modern + Legacy payment deduplication: Zero double counting across modern Payment
           and legacy PaymentTransaction records.
        2. Partial payment handling: Any amount less than total_amount (e.g. ₹20k or ₹40k of
           a ₹60k or ₹100k order) is strictly PARTIALLY_PAID, NEVER FULLY_PAID.
        3. Installment milestone evaluation: Milestones are marked PAID strictly when cumulative
           verified paid funds reach the required threshold. Partial milestone payments remain PENDING.
        4. NEVER updates fulfillment_status.
        5. Deterministic, atomic, and idempotent Decimal arithmetic.
        """
        from decimal import Decimal
        from django.db import transaction
        from django.utils import timezone

        with transaction.atomic():
            # Verified modern payments
            verified_payments = self.payments.filter(status='PAID', verification_status='VERIFIED')
            paid_sum = Decimal('0.00')

            # 1. Deduplication: collect all known references across modern verified payments
            known_identifiers = set()
            modern_paid_by_installment = {}
            for p in verified_payments:
                paid_sum += p.amount
                for ident in [p.payment_id, p.gateway_payment_id, p.reference_number, p.gateway_order_id]:
                    if ident:
                        known_identifiers.add(str(ident).strip().upper())
                if p.installment_id:
                    modern_paid_by_installment[p.installment_id] = (
                        modern_paid_by_installment.get(p.installment_id, Decimal('0.00')) + p.amount
                    )

            # 2. Legacy transactions (status='SUCCESS'): Deduplicate against modern payments
            legacy_txs = self.transactions.filter(status='SUCCESS')
            for t in legacy_txs:
                t_pid = (t.gateway_payment_id or '').strip().upper()
                t_goid = (t.gateway_order_id or '').strip().upper()
                t_idemp = (t.idempotency_key or '').strip().upper()
                legacy_id = f"LEGACY-{t.id}".upper()
                txn_id = f"TXN-{t.id}".upper()

                # Deduplication 1: Explicit identifier match
                if (t_pid and t_pid in known_identifiers) or (t_goid and t_goid in known_identifiers):
                    continue
                if legacy_id in known_identifiers or txn_id in known_identifiers:
                    continue
                if t_idemp and any(t_idemp in ident or ident in t_idemp for ident in known_identifiers):
                    continue

                # Deduplication 2: Same installment already covered by modern verified payment
                if t.installment_id and t.installment_id in modern_paid_by_installment:
                    if modern_paid_by_installment[t.installment_id] >= t.amount:
                        continue

                paid_sum += t.amount

            # Cap paid_sum between 0 and total_amount
            paid_sum = min(self.total_amount, max(Decimal('0.00'), paid_sum))
            self.paid_amount = paid_sum

            # Calculate remaining amount
            self.remaining_amount = max(Decimal('0.00'), self.total_amount - self.paid_amount)

            # Determine payment_status
            # RULE: NEVER mark order as FULLY_PAID when only partial funds (e.g. ₹20k or ₹40k) are paid
            if self.refunded_amount and self.refunded_amount >= self.total_amount:
                self.payment_status = 'REFUNDED'
            elif self.paid_amount >= self.total_amount:
                self.payment_status = 'FULLY_PAID'
            elif self.paid_amount > Decimal('0.00'):
                self.payment_status = 'PARTIALLY_PAID'
            elif self.payments.filter(status='FAILED', is_manual=False).exists() and not self.payments.filter(status__in=['PAID', 'PROCESSING']).exists():
                self.payment_status = 'FAILED'
            elif self.payments.filter(status='PROCESSING').exists():
                self.payment_status = 'PROCESSING'
            else:
                self.payment_status = 'PENDING'

            # Note: order_status is kept solely for legacy compatibility and MUST NOT be
            # mutated by financial or payment calculations.

            # If 3 installments plan, update next_due_date and sync installment statuses mathematically
            if self.payment_plan == 'THREE_INSTALLMENTS' and self.installments.exists():
                installments = list(self.installments.all().order_by('installment_number'))
                cumulative_target = Decimal('0.00')

                for inst in installments:
                    cumulative_target += inst.amount

                    # Milestone is PAID if and only if cumulative verified paid funds reach this milestone
                    if self.paid_amount >= cumulative_target:
                        if inst.status != 'PAID':
                            inst.status = 'PAID'
                            matching_p = verified_payments.filter(installment=inst).first() or verified_payments.order_by('-paid_at', '-created_at').first()
                            matching_t = legacy_txs.filter(installment=inst).first() if not matching_p else None
                            effective_paid_at = (
                                (matching_p.paid_at if matching_p else None) or
                                (matching_t.paid_at if matching_t else None) or
                                timezone.now()
                            )
                            inst.paid_at = effective_paid_at
                            inst.payment_id = (
                                (matching_p.gateway_payment_id or matching_p.reference_number or matching_p.payment_id) if matching_p
                                else (matching_t.gateway_payment_id if matching_t else '')
                            )
                            inst.save(update_fields=['status', 'paid_at', 'payment_id', 'updated_at'])
                    else:
                        # Milestone NOT fully covered (e.g. ₹20k on a ₹33.3k milestone) -> NEVER mark as PAID!
                        if inst.status == 'PAID':
                            is_overdue = bool(inst.due_date and inst.due_date < timezone.now().date())
                            inst.status = 'OVERDUE' if is_overdue else 'PENDING'
                            inst.paid_at = None
                            inst.payment_id = ''
                            inst.save(update_fields=['status', 'paid_at', 'payment_id', 'updated_at'])
                        elif inst.status not in ['OVERDUE', 'CANCELLED']:
                            if inst.due_date and inst.due_date < timezone.now().date():
                                inst.status = 'OVERDUE'
                                inst.save(update_fields=['status', 'updated_at'])

                next_inst = self.installments.filter(status__in=['PENDING', 'OVERDUE']).order_by('installment_number').first()
                self.next_due_date = next_inst.due_date if next_inst else None

            self.save(update_fields=['paid_amount', 'remaining_amount', 'payment_status', 'next_due_date', 'updated_at'])

    def update_financial_status(self):
        """Backward-compatible alias invoking recalculate_financials()."""
        return self.recalculate_financials()


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


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=40, blank=True, default='')
    fulfillment_status = models.CharField(max_length=40, choices=Order.FULFILLMENT_STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='workshop_status_changes')
    admin_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'

    def __str__(self):
        return f"Order #{self.order.order_number}: {self.previous_status} -> {self.fulfillment_status} at {self.created_at}"


class OrderAdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ('MANUAL_PAYMENT_ADDED', 'Manual Payment Added'),
        ('MANUAL_PAYMENT_VERIFIED', 'Manual Payment Verified'),
        ('MANUAL_PAYMENT_REJECTED', 'Manual Payment Rejected'),
        ('PAYMENT_ADJUSTMENT', 'Payment Adjustment'),
        ('REFUND_RECORDED', 'Refund Recorded'),
        ('WORKSHOP_STATUS_CHANGED', 'Workshop Status Changed'),
        ('ADMIN_OVERRIDE', 'Admin Override'),
        ('INSTALLMENT_RESCHEDULED', 'Installment Rescheduled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='admin_audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_audit_logs')
    old_value = models.CharField(max_length=255, blank=True, default='')
    new_value = models.CharField(max_length=255, blank=True, default='')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order Admin Audit Log'
        verbose_name_plural = 'Order Admin Audit Logs'

    def __str__(self):
        return f"Order #{self.order.order_number}: {self.action} by {self.performed_by} at {self.created_at}"

