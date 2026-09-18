from decimal import Decimal
import datetime
from datetime import date, timedelta
from django.utils import timezone
from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.store.models import Product, Category
from apps.bookings.models import (
    Order, Booking, Installment, PaymentTransaction,
    OrderStatusHistory, OrderAdminAuditLog
)
from apps.bookings.services import InstallmentService
from apps.payments.models import Payment
from apps.payments.services import (
    ManualPaymentService, ManualPaymentError, PaymentLedgerService
)


class ArchitectureDecouplingTests(TestCase):
    """
    Comprehensive verification tests for Glory Furniture Hub architecture upgrade:
    1. Complete separation of financial payment_status and workshop fulfillment_status.
    2. Strict 5-stage workshop progress lifecycle.
    3. Admin shipping payment rule and override enforcement.
    4. Full Payment and 3-Installments calculation integrity.
    5. Manual payment lifecycle (recording, unverified state, verification, rejection).
    6. Unified payment ledger deduplication.
    7. Disconnection of checkout from consultation bookings.
    """

    def setUp(self):
        self.category = Category.objects.create(name='Living Room', slug='living-room')
        self.product = Product.objects.create(
            name='Royal Teak Grand Dining Table',
            slug='royal-teak-dining-table',
            category=self.category,
            price=Decimal('100000.00'),
            primary_image='/static/images/card_bed.jpg'
        )
        self.customer = User.objects.create_user(
            username='patron@example.com',
            email='patron@example.com',
            password='securePassword123'
        )
        self.admin = User.objects.create_superuser(
            username='admin@gloryfurniture.com',
            email='admin@gloryfurniture.com',
            password='adminPassword123'
        )
        self.client = Client()

    def test_full_payment_order_financial_recalculation(self):
        """Full Payment order starts PENDING, becomes FULLY_PAID on settlement, fulfillment untouched."""
        order = Order.objects.create(
            user=self.customer,
            customer_name='Maharaja Patron',
            email='patron@example.com',
            phone='+91 98765 43210',
            product=self.product,
            product_name=self.product.name,
            total_amount=Decimal('100000.00'),
            paid_amount=Decimal('0.00'),
            remaining_amount=Decimal('100000.00'),
            unit_price=Decimal('100000.00'),
            payment_plan='FULL_PAYMENT',
            payment_status='PENDING',
            fulfillment_status='CONFIRMED',
        )
        self.assertEqual(order.payment_status, 'PENDING')
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')
        self.assertEqual(order.remaining_amount, Decimal('100000.00'))

        # Record and verify manual full payment
        payment = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('100000.00'),
            payment_method='UPI',
            reference_number='UPI-FULL-9988',
            admin_user=self.admin
        )
        self.assertEqual(payment.verification_status, 'PENDING_VERIFICATION')
        order.refresh_from_db()
        # Unverified payment does NOT count towards paid balance
        self.assertEqual(order.paid_amount, Decimal('0.00'))
        self.assertEqual(order.payment_status, 'PENDING')

        # Verify payment
        ManualPaymentService.verify_manual_payment(payment.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        self.assertEqual(order.paid_amount, Decimal('100000.00'))
        self.assertEqual(order.remaining_amount, Decimal('0.00'))
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        # Crucial: fulfillment_status MUST remain CONFIRMED
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')

    def test_three_installments_lifecycle(self):
        """3-Installment plan: partial payments do not alter fulfillment stages."""
        order = InstallmentService.create_installment_order({
            'user': self.customer,
            'customer_name': 'Raja Patron',
            'email': 'patron@example.com',
            'phone': '+91 98765 43210',
            'product': self.product,
            'product_name': self.product.name,
            'total_amount': Decimal('100000.00'),
            'payment_plan': 'THREE_INSTALLMENTS'
        })
        self.assertEqual(order.payment_status, 'PENDING')
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')
        self.assertEqual(order.installments.count(), 3)

        inst1, inst2, inst3 = order.installments.all().order_by('installment_number')

        # Pay Installment 1
        pay1 = ManualPaymentService.record_manual_payment(
            order=order,
            amount=inst1.amount,
            payment_method='BANK_TRANSFER',
            installment=inst1,
            reference_number='NEFT-INST1-001',
            admin_user=self.admin
        )
        ManualPaymentService.verify_manual_payment(pay1.payment_id, admin_user=self.admin)

        order.refresh_from_db()
        inst1.refresh_from_db()
        self.assertEqual(inst1.status, 'PAID')
        self.assertEqual(order.paid_amount, inst1.amount)
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')

        # Pay Installment 2
        pay2 = ManualPaymentService.record_manual_payment(
            order=order,
            amount=inst2.amount,
            payment_method='CASH',
            installment=inst2,
            reference_number='CASH-INST2-002',
            admin_user=self.admin
        )
        ManualPaymentService.verify_manual_payment(pay2.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')

        # Pay Installment 3 (Final)
        pay3 = ManualPaymentService.record_manual_payment(
            order=order,
            amount=inst3.amount,
            payment_method='UPI',
            installment=inst3,
            reference_number='UPI-INST3-003',
            admin_user=self.admin
        )
        ManualPaymentService.verify_manual_payment(pay3.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        self.assertEqual(order.paid_amount, Decimal('100000.00'))
        self.assertEqual(order.remaining_amount, Decimal('0.00'))
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        # Fulfillment status remains untouched
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')

    def test_manual_payment_rejection(self):
        """Rejected manual payment does not credit balance and logs audit reason."""
        order = Order.objects.create(
            user=self.customer,
            customer_name='Devi Patron',
            email='devi@example.com',
            phone='+91 98765 00000',
            product=self.product,
            product_name=self.product.name,
            total_amount=Decimal('50000.00'),
            paid_amount=Decimal('0.00'),
            remaining_amount=Decimal('50000.00'),
            unit_price=Decimal('50000.00'),
            payment_plan='FULL_PAYMENT',
            payment_status='PENDING',
            fulfillment_status='CONFIRMED',
        )

        payment = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('50000.00'),
            payment_method='OFFLINE',
            reference_number='POS-REJECT-01',
            admin_user=self.admin
        )
        self.assertEqual(payment.verification_status, 'PENDING_VERIFICATION')

        ManualPaymentService.reject_manual_payment(
            payment.payment_id,
            admin_user=self.admin,
            rejection_reason='Card swipe bounced on showroom terminal'
        )

        payment.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(payment.verification_status, 'REJECTED')
        self.assertEqual(payment.status, 'FAILED')
        self.assertEqual(order.paid_amount, Decimal('0.00'))
        self.assertEqual(order.remaining_amount, Decimal('50000.00'))
        self.assertEqual(order.payment_status, 'PENDING')

        # Audit log created
        log = OrderAdminAuditLog.objects.filter(order=order, action='MANUAL_PAYMENT_REJECTED').first()
        self.assertIsNotNone(log)
        self.assertIn('Card swipe bounced', log.notes)

    def test_manual_payment_overpayment_rejected(self):
        """Attempting to record a manual payment greater than remaining balance raises error."""
        order = Order.objects.create(
            user=self.customer,
            customer_name='Patron Test',
            email='patron@example.com',
            phone='+91 98765 11111',
            product=self.product,
            product_name=self.product.name,
            total_amount=Decimal('20000.00'),
            paid_amount=Decimal('0.00'),
            remaining_amount=Decimal('20000.00'),
            unit_price=Decimal('20000.00'),
            payment_plan='FULL_PAYMENT',
            payment_status='PENDING',
        )

        with self.assertRaises(ManualPaymentError):
            ManualPaymentService.record_manual_payment(
                order=order,
                amount=Decimal('25000.00'),
                payment_method='CASH',
                admin_user=self.admin
            )

    def test_admin_shipping_payment_rule_and_override(self):
        """Attempting to ship an unpaid order requires explicit Admin Override with reason."""
        order = Order.objects.create(
            user=self.customer,
            customer_name='Unpaid Patron',
            email='unpaid@example.com',
            phone='+91 98765 22222',
            product=self.product,
            product_name=self.product.name,
            total_amount=Decimal('60000.00'),
            paid_amount=Decimal('20000.00'),
            remaining_amount=Decimal('40000.00'),
            unit_price=Decimal('60000.00'),
            payment_plan='THREE_INSTALLMENTS',
            payment_status='PARTIALLY_PAID',
            fulfillment_status='IN_PRODUCTION',
        )

        self.client.force_login(self.admin)

        # 1. Attempt transition to SHIPPED without override
        response = self.client.post('/admin/orders/', {
            'action': 'update_fulfillment_status',
            'order_id': order.id,
            'fulfillment_status': 'SHIPPED',
        }, follow=True)
        order.refresh_from_db()
        # Must NOT be updated to SHIPPED
        self.assertEqual(order.fulfillment_status, 'IN_PRODUCTION')

        # 2. Attempt transition to SHIPPED WITH authorized override
        response = self.client.post('/admin/orders/', {
            'action': 'update_fulfillment_status',
            'order_id': order.id,
            'fulfillment_status': 'SHIPPED',
            'override_shipping_payment': 'true',
            'override_reason': 'Authorized by managing director for Cash on Delivery at doorstep'
        }, follow=True)
        order.refresh_from_db()
        self.assertEqual(order.fulfillment_status, 'SHIPPED')

        # Check OrderStatusHistory and OrderAdminAuditLog
        history = OrderStatusHistory.objects.filter(order=order, fulfillment_status='SHIPPED').first()
        self.assertIsNotNone(history)
        self.assertIn('SHIPPING OVERRIDE', history.admin_notes)

        audit = OrderAdminAuditLog.objects.filter(order=order, action='ADMIN_OVERRIDE').first()
        self.assertIsNotNone(audit)
        self.assertIn('Cash on Delivery', audit.notes)

    def test_strictly_five_workshop_stages(self):
        """Workshop status rejects stages not in the 5 official craftsmanship stages."""
        order = Order.objects.create(
            user=self.customer,
            customer_name='Stage Test',
            email='stage@example.com',
            phone='+91 98765 33333',
            product=self.product,
            product_name=self.product.name,
            total_amount=Decimal('30000.00'),
            paid_amount=Decimal('30000.00'),
            remaining_amount=Decimal('0.00'),
            unit_price=Decimal('30000.00'),
            payment_plan='FULL_PAYMENT',
            payment_status='FULLY_PAID',
            fulfillment_status='CONFIRMED',
        )

        self.client.force_login(self.admin)

        # Invalid stage 'CANCELLED' or 'REFUNDED'
        response = self.client.post('/admin/orders/', {
            'action': 'update_fulfillment_status',
            'order_id': order.id,
            'fulfillment_status': 'CANCELLED',
        }, follow=True)
        order.refresh_from_db()
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')

        # Valid transition through the 5 stages
        for stage in ['IN_PRODUCTION', 'SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']:
            self.client.post('/admin/orders/', {
                'action': 'update_fulfillment_status',
                'order_id': order.id,
                'fulfillment_status': stage,
            }, follow=True)
            order.refresh_from_db()
            self.assertEqual(order.fulfillment_status, stage)

    def test_unified_ledger_deduplication(self):
        """Unified ledger deduplicates legacy and modern records with the same reference."""
        order = Order.objects.create(
            user=self.customer,
            customer_name='Ledger Patron',
            email='ledger@example.com',
            phone='+91 98765 44444',
            product=self.product,
            product_name=self.product.name,
            total_amount=Decimal('40000.00'),
            paid_amount=Decimal('40000.00'),
            remaining_amount=Decimal('0.00'),
            unit_price=Decimal('40000.00'),
            payment_plan='FULL_PAYMENT',
            payment_status='FULLY_PAID',
        )

        # Create modern payment
        Payment.objects.create(
            order=order,
            customer=self.customer,
            payment_type='FULL',
            amount=Decimal('40000.00'),
            gateway='Cashfree',
            gateway_payment_id='CF-DUPLICATE-REF-101',
            status='PAID',
            verification_status='VERIFIED',
        )

        # Create legacy transaction with identical reference
        PaymentTransaction.objects.create(
            order=order,
            amount=Decimal('40000.00'),
            gateway='Cashfree',
            gateway_payment_id='CF-DUPLICATE-REF-101',
            status='SUCCESS',
        )

        ledger = PaymentLedgerService.get_order_transactions(order)
        # Deduplication must return exactly 1 item, prioritizing modern Payment
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]['reference'], 'CF-DUPLICATE-REF-101')
        self.assertEqual(ledger[0]['source'], 'Cashfree')

    def test_ecommerce_checkout_does_not_create_consultation_booking(self):
        """E-commerce checkout must not insert fake consultation bookings."""
        initial_bookings_count = Booking.objects.count()

        # Simulate checkout via client
        self.client.force_login(self.customer)
        session = self.client.session
        session['glory_cart'] = [{
            'id': self.product.id,
            'name': self.product.name,
            'price': float(self.product.price),
            'quantity': 1,
            'size': 'Standard',
            'wood': 'Grade-A Burma Teak'
        }]
        session.save()

        response = self.client.post('/booking/summary/', {
            'fullName': 'Ganesh Patron',
            'email': 'ganesh@example.com',
            'phone': '+91 98765 55555',
            'address': 'Madhapur, Hyderabad',
            'payment_plan': 'FULL_PAYMENT'
        }, follow=True)

        # No consultation bookings created
        self.assertEqual(Booking.objects.count(), initial_bookings_count)

        # Order created with clean decoupled status
        order = Order.objects.filter(user=self.customer).first()
        self.assertIsNotNone(order)
        self.assertIsNone(order.booking)
        self.assertEqual(order.payment_status, 'PENDING')
        self.assertEqual(order.fulfillment_status, 'CONFIRMED')

    def test_modern_plus_legacy_calculation_no_double_counting(self):
        """
        Requirement 1: Modern + Legacy payment calculation MUST NOT double count
        records sharing the same reference, gateway ID, or installment.
        """
        order = Order.objects.create(
            user=self.customer,
            customer_name='Double Count Guard Test',
            email='guard@example.com',
            phone='+91 98765 44444',
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal('60000.00'),
            quantity=1,
            total_amount=Decimal('60000.00'),
            payment_status='PENDING',
            fulfillment_status='CONFIRMED',
        )

        # Legacy transaction
        legacy_tx = PaymentTransaction.objects.create(
            order=order,
            amount=Decimal('20000.00'),
            gateway='Cashfree',
            gateway_payment_id='CF-TXN-SHARED-999',
            status='SUCCESS',
            paid_at=timezone.now() - datetime.timedelta(days=10),
        )

        # Modern verified payment mirroring the legacy transaction
        modern_dup = Payment.objects.create(
            order=order,
            customer=self.customer,
            payment_type='FULL',
            amount=Decimal('20000.00'),
            currency='INR',
            gateway='Cashfree',
            gateway_payment_id='CF-TXN-SHARED-999',
            reference_number='CF-TXN-SHARED-999',
            status='PAID',
            verification_status='VERIFIED',
            paid_at=legacy_tx.paid_at,
        )

        # Distinct new modern manual payment
        modern_new = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('20000.00'),
            payment_method='UPI',
            reference_number='UPI-DISTINCT-888',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(modern_new.payment_id, admin_user=self.admin)

        order.refresh_from_db()
        # MUST sum to ₹40,000, NOT ₹60,000 (duplicate CF-TXN-SHARED-999 counted once)
        self.assertEqual(order.paid_amount, Decimal('40000.00'))
        self.assertEqual(order.remaining_amount, Decimal('20000.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')

        ledger = PaymentLedgerService.get_order_transactions(order)
        # Deduplicated ledger must have exactly 2 entries (not 3)
        self.assertEqual(len(ledger), 2)
        refs = [e['reference'] for e in ledger]
        self.assertIn('CF-TXN-SHARED-999', refs)
        self.assertIn('UPI-DISTINCT-888', refs)

    def test_installment_partial_20k_40k_never_marked_paid(self):
        """
        Requirement 2: On a 3-installment plan (e.g. ₹60k total = 3 x ₹20k),
        paying ₹20k or ₹40k must NEVER mark the order as FULLY_PAID or PAID.
        """
        order = Order.objects.create(
            user=self.customer,
            customer_name='Milestone Partial Test',
            email='milestone@example.com',
            phone='+91 98765 33333',
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal('60000.00'),
            quantity=1,
            total_amount=Decimal('60000.00'),
            payment_plan='THREE_INSTALLMENTS',
            payment_status='PENDING',
            order_status='PENDING_PAYMENT',
            fulfillment_status='CONFIRMED',
        )
        today = timezone.now().date()
        inst1 = Installment.objects.create(order=order, installment_number=1, amount=Decimal('20000.00'), due_date=today, status='PENDING')
        inst2 = Installment.objects.create(order=order, installment_number=2, amount=Decimal('20000.00'), due_date=today + datetime.timedelta(days=30), status='PENDING')
        inst3 = Installment.objects.create(order=order, installment_number=3, amount=Decimal('20000.00'), due_date=today + datetime.timedelta(days=60), status='PENDING')

        # 1. Pay ₹20,000 (Installment 1)
        p1 = ManualPaymentService.record_manual_payment(
            order=order,
            installment_id=inst1.id,
            amount=Decimal('20000.00'),
            payment_method='UPI',
            reference_number='PAY-PART-20K',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p1.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        inst1.refresh_from_db()
        inst2.refresh_from_db()
        inst3.refresh_from_db()

        # Check: ₹20k paid -> ORDER MUST BE PARTIALLY_PAID, NEVER FULLY_PAID; order_status must NOT be changed
        self.assertEqual(order.paid_amount, Decimal('20000.00'))
        self.assertEqual(order.remaining_amount, Decimal('40000.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        self.assertEqual(order.order_status, 'PENDING_PAYMENT')
        self.assertNotEqual(order.payment_status, 'FULLY_PAID')
        self.assertEqual(inst1.status, 'PAID')
        self.assertEqual(inst2.status, 'PENDING')
        self.assertEqual(inst3.status, 'PENDING')

        # 2. Pay another ₹20,000 (total ₹40,000 paid)
        p2 = ManualPaymentService.record_manual_payment(
            order=order,
            installment_id=inst2.id,
            amount=Decimal('20000.00'),
            payment_method='BANK_TRANSFER',
            reference_number='PAY-PART-40K',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p2.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        inst1.refresh_from_db()
        inst2.refresh_from_db()
        inst3.refresh_from_db()

        # Check: ₹40k paid -> ORDER MUST STILL BE PARTIALLY_PAID, NEVER FULLY_PAID; order_status remains untouched
        self.assertEqual(order.paid_amount, Decimal('40000.00'))
        self.assertEqual(order.remaining_amount, Decimal('20000.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        self.assertEqual(order.order_status, 'PENDING_PAYMENT')
        self.assertNotEqual(order.payment_status, 'FULLY_PAID')
        self.assertEqual(inst1.status, 'PAID')
        self.assertEqual(inst2.status, 'PAID')
        self.assertEqual(inst3.status, 'PENDING')
        self.assertNotEqual(inst3.status, 'PAID')

        # 3. Pay final ₹20,000 (total ₹60,000) -> NOW order is FULLY_PAID; order_status remains untouched
        p3 = ManualPaymentService.record_manual_payment(
            order=order,
            installment_id=inst3.id,
            amount=Decimal('20000.00'),
            payment_method='CASH',
            reference_number='PAY-FINAL-60K',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p3.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        inst3.refresh_from_db()
        self.assertEqual(order.paid_amount, Decimal('60000.00'))
        self.assertEqual(order.remaining_amount, Decimal('0.00'))
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        self.assertEqual(order.order_status, 'PENDING_PAYMENT')
        self.assertEqual(inst3.status, 'PAID')

    def test_installment_underpayment_never_marked_paid(self):
        """
        Requirement 2: When an installment is ₹33,334 (e.g. ₹100k order),
        paying ₹20k towards it must NEVER mark that installment as PAID.
        """
        order = Order.objects.create(
            user=self.customer,
            customer_name='Underpayment Test',
            email='underpay@example.com',
            phone='+91 98765 22222',
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal('100000.00'),
            quantity=1,
            total_amount=Decimal('100000.00'),
            payment_plan='THREE_INSTALLMENTS',
            payment_status='PENDING',
            fulfillment_status='CONFIRMED',
        )
        today = timezone.now().date()
        inst1 = Installment.objects.create(order=order, installment_number=1, amount=Decimal('33334.00'), due_date=today, status='PENDING')
        inst2 = Installment.objects.create(order=order, installment_number=2, amount=Decimal('33333.00'), due_date=today + datetime.timedelta(days=30), status='PENDING')
        inst3 = Installment.objects.create(order=order, installment_number=3, amount=Decimal('33333.00'), due_date=today + datetime.timedelta(days=60), status='PENDING')

        # Pay only ₹20,000 towards Installment 1 (which requires ₹33,334)
        p = ManualPaymentService.record_manual_payment(
            order=order,
            installment_id=inst1.id,
            amount=Decimal('20000.00'),
            payment_method='UPI',
            reference_number='UPI-UNDERPAY-20K',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        inst1.refresh_from_db()

        # Check: ₹20k paid on ₹33,334 installment MUST NOT be marked PAID
        self.assertEqual(order.paid_amount, Decimal('20000.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        self.assertEqual(inst1.status, 'PENDING')
        self.assertNotEqual(inst1.status, 'PAID')

        # Pay another ₹20,000 (total ₹40,000 paid)
        p2 = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('20000.00'),
            payment_method='UPI',
            reference_number='UPI-NEXT-20K',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p2.payment_id, admin_user=self.admin)
        order.refresh_from_db()
        inst1.refresh_from_db()
        inst2.refresh_from_db()

        # Cumulative paid is ₹40,000:
        # Milestone 1 (₹33,334) is now reached -> PAID
        # Milestone 2 (cumulative ₹66,667) is NOT reached (₹40,000 < ₹66,667) -> PENDING (NEVER PAID)
        self.assertEqual(order.paid_amount, Decimal('40000.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        self.assertEqual(inst1.status, 'PAID')
        self.assertEqual(inst2.status, 'PENDING')
        self.assertNotEqual(inst2.status, 'PAID')

    def test_payment_date_vs_created_date_financial_history(self):
        """
        Requirement 3: Payment date (paid_at) must preserve the actual date
        the payment occurred, while created_at captures when it was recorded in the database.
        """
        order = Order.objects.create(
            user=self.customer,
            customer_name='Date Preservation Test',
            email='dates@example.com',
            phone='+91 98765 11110',
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal('50000.00'),
            quantity=1,
            total_amount=Decimal('50000.00'),
            payment_status='PENDING',
            fulfillment_status='CONFIRMED',
        )

        historical_date = timezone.now() - datetime.timedelta(days=7)

        payment = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('50000.00'),
            payment_method='BANK_TRANSFER',
            reference_number='NEFT-HISTORICAL-001',
            payment_date=historical_date,
            notes='Direct NEFT received last week',
            admin_user=self.admin,
        )

        payment.refresh_from_db()
        # paid_at preserves the historical payment date
        self.assertIsNotNone(payment.paid_at)
        self.assertEqual(payment.paid_at.date(), historical_date.date())
        # created_at captures today's insertion timestamp
        self.assertEqual(payment.created_at.date(), timezone.now().date())

        # Admin verifies payment today
        ManualPaymentService.verify_manual_payment(payment.payment_id, admin_user=self.admin)
        payment.refresh_from_db()
        # Verification date is today
        self.assertEqual(payment.verified_at.date(), timezone.now().date())
        # CRUCIAL: paid_at STILL preserves the historical payment date!
        self.assertEqual(payment.paid_at.date(), historical_date.date())

        # Ledger exposes both dates
        ledger = PaymentLedgerService.get_order_transactions(order)
        self.assertEqual(len(ledger), 1)
        self.assertEqual(ledger[0]['paid_at'].date(), historical_date.date())
        self.assertEqual(ledger[0]['created_at'].date(), timezone.now().date())

    def test_recalculate_financials_does_not_mutate_order_status_or_fulfillment_status(self):
        """
        Regression Test (Final Architecture):
        Proves:
        1. payment_status can change to PARTIALLY_PAID
        2. order_status is NOT changed by recalculate_financials()
        3. fulfillment_status remains unchanged
        4. payment_status can become FULLY_PAID
        5. fulfillment_status remains unchanged
        6. workshop updates do not change payment_status
        """
        order = Order.objects.create(
            user=self.customer,
            customer_name='Decoupled Architecture Test',
            email='decoupled@example.com',
            phone='+91 98765 00000',
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal('50000.00'),
            quantity=1,
            total_amount=Decimal('50000.00'),
            payment_status='PENDING',
            order_status='LEGACY_INITIAL_STATE',
            fulfillment_status='CONFIRMED',
        )

        initial_order_status = order.order_status
        initial_fulfillment_status = order.fulfillment_status
        self.assertEqual(order.payment_status, 'PENDING')
        self.assertEqual(initial_order_status, 'LEGACY_INITIAL_STATE')
        self.assertEqual(initial_fulfillment_status, 'CONFIRMED')

        # 1. Record & verify partial payment (₹20,000 of ₹50,000)
        p1 = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('20000.00'),
            payment_method='UPI',
            reference_number='UPI-PART-20K-REG',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p1.payment_id, admin_user=self.admin)
        order.refresh_from_db()

        # Proves 1: payment_status changed to PARTIALLY_PAID
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        # Proves 2: order_status is NOT changed by recalculate_financials()
        self.assertEqual(order.order_status, initial_order_status)
        # Proves 3: fulfillment_status remains unchanged
        self.assertEqual(order.fulfillment_status, initial_fulfillment_status)

        # 2. Record & verify remaining payment (₹30,000)
        p2 = ManualPaymentService.record_manual_payment(
            order=order,
            amount=Decimal('30000.00'),
            payment_method='BANK_TRANSFER',
            reference_number='BANK-FINAL-30K-REG',
            admin_user=self.admin,
        )
        ManualPaymentService.verify_manual_payment(p2.payment_id, admin_user=self.admin)
        order.refresh_from_db()

        # Proves 4: payment_status became FULLY_PAID
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        # Proves 2 (continued): order_status is STILL NOT changed by recalculate_financials()
        self.assertEqual(order.order_status, initial_order_status)
        # Proves 5: fulfillment_status remains unchanged
        self.assertEqual(order.fulfillment_status, initial_fulfillment_status)

        # Proves 6: workshop updates do not change payment_status
        order.fulfillment_status = 'IN_PRODUCTION'
        order.save(update_fields=['fulfillment_status', 'updated_at'])
        order.refresh_from_db()
        self.assertEqual(order.fulfillment_status, 'IN_PRODUCTION')
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        self.assertEqual(order.order_status, initial_order_status)

        order.fulfillment_status = 'SHIPPED'
        order.save(update_fields=['fulfillment_status', 'updated_at'])
        order.refresh_from_db()
        self.assertEqual(order.fulfillment_status, 'SHIPPED')
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        self.assertEqual(order.order_status, initial_order_status)
