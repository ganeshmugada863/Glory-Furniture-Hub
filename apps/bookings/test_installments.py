import json
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase, Client
from django.utils import timezone
from apps.bookings.models import Order, Installment, PaymentTransaction, InstallmentRescheduleAudit, Booking
from apps.bookings.services import (
    InstallmentService, PaymentService, RescheduleService,
    InstallmentCalculationError, InstallmentRescheduleError
)
from apps.store.models import Product, Category


class ThreeInstallmentMathTests(TestCase):
    """
    Test exact decimal mathematics and remainder allocation to 3rd installment.
    Zero floating-point arithmetic.
    """

    def test_inr_100k_math(self):
        # 100,000 -> 33,333 + 33,333 + 33,334
        insts = InstallmentService.calculate_three_installments(Decimal('100000.00'))
        self.assertEqual(insts[0], Decimal('33333.00'))
        self.assertEqual(insts[1], Decimal('33333.00'))
        self.assertEqual(insts[2], Decimal('33334.00'))
        self.assertEqual(sum(insts), Decimal('100000.00'))

    def test_inr_75k_math(self):
        # 75,000 -> 25,000 x 3
        insts = InstallmentService.calculate_three_installments(75000)
        self.assertEqual(insts[0], Decimal('25000.00'))
        self.assertEqual(insts[1], Decimal('25000.00'))
        self.assertEqual(insts[2], Decimal('25000.00'))
        self.assertEqual(sum(insts), Decimal('75000.00'))

    def test_inr_10k_math(self):
        # 10,000 -> 3,333 + 3,333 + 3,334
        insts = InstallmentService.calculate_three_installments(10000)
        self.assertEqual(insts[0], Decimal('3333.00'))
        self.assertEqual(insts[1], Decimal('3333.00'))
        self.assertEqual(insts[2], Decimal('3334.00'))
        self.assertEqual(sum(insts), Decimal('10000.00'))

    def test_inr_999_math(self):
        # 999 -> 333 x 3
        insts = InstallmentService.calculate_three_installments(999)
        self.assertEqual(insts[0], Decimal('333.00'))
        self.assertEqual(insts[1], Decimal('333.00'))
        self.assertEqual(insts[2], Decimal('333.00'))
        self.assertEqual(sum(insts), Decimal('999.00'))

    def test_arbitrary_odd_amount(self):
        # e.g. 50,000 -> 16,666 + 16,666 + 16,668
        insts = InstallmentService.calculate_three_installments(50000)
        self.assertEqual(insts[0], Decimal('16666.00'))
        self.assertEqual(insts[1], Decimal('16666.00'))
        self.assertEqual(insts[2], Decimal('16668.00'))
        self.assertEqual(sum(insts), Decimal('50000.00'))

    def test_zero_or_negative_rejected(self):
        with self.assertRaises(InstallmentCalculationError):
            InstallmentService.calculate_three_installments(0)
        with self.assertRaises(InstallmentCalculationError):
            InstallmentService.calculate_three_installments(-500)


class ThreeInstallmentOrderFlowTests(TestCase):
    """
    Test Order creation, installment lifecycle, and full progression to FULLY_PAID.
    """

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Beds', slug='beds')
        self.product = Product.objects.create(
            name='Royal Teak Bed',
            price=Decimal('75000.00'),
            category=self.category,
            material='Solid Burma Teak Wood'
        )
        self.booking = Booking.objects.create(
            customer_name='Ganesh Mugada',
            email='ganesh@test.com',
            phone='+919876543210',
            address='Jubilee Hills, Hyderabad',
            preferred_date=timezone.now().date() + timedelta(days=3),
            consultation_type='Product Order'
        )

    def test_order_creation_with_three_installments(self):
        order = InstallmentService.create_order_with_installments({
            'booking': self.booking,
            'customer_name': 'Ganesh Mugada',
            'email': 'ganesh@test.com',
            'phone': '+919876543210',
            'shipping_address': 'Jubilee Hills, Hyderabad',
            'product': self.product,
            'product_name': self.product.name,
            'total_amount': Decimal('75000.00'),
            'payment_plan': 'THREE_INSTALLMENTS'
        })

        self.assertEqual(order.payment_plan, 'THREE_INSTALLMENTS')
        self.assertEqual(order.payment_status, 'PENDING_PAYMENT')
        self.assertEqual(order.paid_amount, Decimal('0.00'))
        self.assertEqual(order.remaining_amount, Decimal('75000.00'))

        installments = list(order.installments.all().order_by('installment_number'))
        self.assertEqual(len(installments), 3)

        # Check amounts
        self.assertEqual(installments[0].amount, Decimal('25000.00'))
        self.assertEqual(installments[1].amount, Decimal('25000.00'))
        self.assertEqual(installments[2].amount, Decimal('25000.00'))

        # Check due dates (Day 0, Day 30, Day 60)
        today = timezone.now().date()
        self.assertEqual(installments[0].due_date, today)
        self.assertEqual(installments[1].due_date, today + timedelta(days=30))
        self.assertEqual(installments[2].due_date, today + timedelta(days=60))

        # Check payment eligibility: only inst 1 is eligible initially
        self.assertTrue(installments[0].is_eligible_for_payment)
        self.assertFalse(installments[1].is_eligible_for_payment)
        self.assertFalse(installments[2].is_eligible_for_payment)

    def test_payment_progression_across_three_installments(self):
        order = InstallmentService.create_order_with_installments({
            'booking': self.booking,
            'customer_name': 'Ganesh Mugada',
            'email': 'ganesh@test.com',
            'phone': '+919876543210',
            'shipping_address': 'Jubilee Hills, Hyderabad',
            'product': self.product,
            'product_name': self.product.name,
            'total_amount': Decimal('100000.00'),
            'payment_plan': 'THREE_INSTALLMENTS'
        })
        inst1, inst2, inst3 = order.installments.all().order_by('installment_number')

        # 1. Pay Installment #1 (33,333)
        success, txn1, msg = PaymentService.process_payment(
            order=order,
            installment_id=inst1.id,
            amount=inst1.amount,
            gateway='UPI',
            gateway_payment_id='PAY-TEST-001',
            idempotency_key='IDEMP-TEST-001'
        )
        self.assertTrue(success)
        order.refresh_from_db()
        inst1.refresh_from_db()
        inst2.refresh_from_db()

        self.assertEqual(inst1.status, 'PAID')
        self.assertIsNotNone(inst1.paid_at)
        self.assertEqual(order.paid_amount, Decimal('33333.00'))
        self.assertEqual(order.remaining_amount, Decimal('66667.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')

        # Now Installment #2 should be eligible
        self.assertTrue(inst2.is_eligible_for_payment)
        self.assertFalse(inst3.is_eligible_for_payment)

        # 2. Idempotency test: Re-submitting same idempotency key does not re-charge or double-count
        success_dup, txn_dup, msg_dup = PaymentService.process_payment(
            order=order,
            installment_id=inst1.id,
            amount=inst1.amount,
            gateway='UPI',
            gateway_payment_id='PAY-TEST-001',
            idempotency_key='IDEMP-TEST-001'
        )
        order.refresh_from_db()
        self.assertEqual(order.paid_amount, Decimal('33333.00'))
        self.assertEqual(txn_dup.id, txn1.id)

        # 3. Pay Installment #2 (33,333)
        success, txn2, msg = PaymentService.process_payment(
            order=order,
            installment_id=inst2.id,
            amount=inst2.amount,
            gateway='Credit Card',
            gateway_payment_id='PAY-TEST-002',
            idempotency_key='IDEMP-TEST-002'
        )
        order.refresh_from_db()
        inst2.refresh_from_db()
        inst3.refresh_from_db()

        self.assertEqual(inst2.status, 'PAID')
        self.assertEqual(order.paid_amount, Decimal('66666.00'))
        self.assertEqual(order.remaining_amount, Decimal('33334.00'))
        self.assertEqual(order.payment_status, 'PARTIALLY_PAID')
        self.assertTrue(inst3.is_eligible_for_payment)

        # 4. Pay Installment #3 (33,334)
        success, txn3, msg = PaymentService.process_payment(
            order=order,
            installment_id=inst3.id,
            amount=inst3.amount,
            gateway='NetBanking',
            gateway_payment_id='PAY-TEST-003',
            idempotency_key='IDEMP-TEST-003'
        )
        order.refresh_from_db()
        inst3.refresh_from_db()

        self.assertEqual(inst3.status, 'PAID')
        self.assertEqual(order.paid_amount, Decimal('100000.00'))
        self.assertEqual(order.remaining_amount, Decimal('0.00'))
        self.assertEqual(order.payment_status, 'FULLY_PAID')
        self.assertIsNone(order.next_due_installment)


class RescheduleServiceAndAuditTests(TestCase):
    """
    Test Admin Due Date Control, Sequential Validation, Mandatory Justification,
    and Immutable Audit Logging.
    """

    def setUp(self):
        self.order = InstallmentService.create_order_with_installments({
            'customer_name': 'Test Customer',
            'email': 'customer@test.com',
            'phone': '+919988776655',
            'total_amount': Decimal('75000.00'),
            'payment_plan': 'THREE_INSTALLMENTS'
        })
        self.inst1, self.inst2, self.inst3 = self.order.installments.all().order_by('installment_number')

    def test_successful_reschedule_with_audit_trail(self):
        old_due = self.inst2.due_date
        new_due = old_due + timedelta(days=10)
        reason = "Customer travel request: 10-day extension granted by Workshop Director"

        success, audit, msg = RescheduleService.reschedule_installment(
            installment_id=self.inst2.id,
            new_due_date=new_due,
            reason=reason,
            changed_by="Master Studio Admin",
            notify_customer=True
        )

        self.assertTrue(success)
        self.inst2.refresh_from_db()
        self.assertEqual(self.inst2.due_date, new_due)

        # Verify Immutable Audit Entry
        self.assertIsNotNone(audit)
        self.assertEqual(audit.order, self.order)
        self.assertEqual(audit.installment, self.inst2)
        self.assertEqual(audit.old_due_date, old_due)
        self.assertEqual(audit.new_due_date, new_due)
        self.assertEqual(audit.reason, reason)
        self.assertEqual(audit.changed_by, "Master Studio Admin")
        self.assertTrue(audit.customer_notified)

        # Audit count
        audits_count = InstallmentRescheduleAudit.objects.filter(order=self.order).count()
        self.assertEqual(audits_count, 1)

    def test_reschedule_requires_mandatory_reason(self):
        new_due = self.inst2.due_date + timedelta(days=5)
        with self.assertRaises(InstallmentRescheduleError):
            RescheduleService.reschedule_installment(
                installment_id=self.inst2.id,
                new_due_date=new_due,
                reason="",
                changed_by="Admin"
            )

    def test_reschedule_enforces_chronological_sequence(self):
        # Setting Installment #2 due date before Installment #1
        invalid_early_date = self.inst1.due_date - timedelta(days=2)
        with self.assertRaises(InstallmentRescheduleError):
            RescheduleService.reschedule_installment(
                installment_id=self.inst2.id,
                new_due_date=invalid_early_date,
                reason="Invalid early date test",
                changed_by="Admin"
            )

        # Setting Installment #2 due date after Installment #3
        invalid_late_date = self.inst3.due_date + timedelta(days=5)
        with self.assertRaises(InstallmentRescheduleError):
            RescheduleService.reschedule_installment(
                installment_id=self.inst2.id,
                new_due_date=invalid_late_date,
                reason="Invalid late date test",
                changed_by="Admin"
            )

    def test_cannot_reschedule_paid_installment(self):
        PaymentService.process_payment(
            order=self.order,
            installment_id=self.inst1.id,
            amount=self.inst1.amount,
            gateway='UPI',
            gateway_payment_id='PAY-PAID-01',
            idempotency_key='IDEMP-PAID-01'
        )
        self.inst1.refresh_from_db()
        self.assertEqual(self.inst1.status, 'PAID')

        with self.assertRaises(InstallmentRescheduleError):
            RescheduleService.reschedule_installment(
                installment_id=self.inst1.id,
                new_due_date=self.inst1.due_date + timedelta(days=5),
                reason="Attempting to reschedule paid installment",
                changed_by="Admin"
            )


class SecurityAndAccessControlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = InstallmentService.create_order_with_installments({
            'customer_name': 'Security Test User',
            'email': 'security@test.com',
            'phone': '+919999988888',
            'total_amount': Decimal('75000.00'),
            'payment_plan': 'THREE_INSTALLMENTS'
        })
        self.inst1, self.inst2, self.inst3 = self.order.installments.all().order_by('installment_number')

    def test_customer_cannot_pay_out_of_sequence(self):
        response = self.client.get(f"/installment/{self.inst2.id}/pay/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("not eligible for payment yet", response.content.decode())

    def test_non_admin_cannot_access_admin_order_detail(self):
        response = self.client.get(f"/admin-portal/order/{self.order.id}/")
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_access_admin_reschedule_api(self):
        response = self.client.post(
            f"/api/orders/{self.order.id}/installments/{self.inst2.id}/reschedule/",
            data=json.dumps({
                'new_due_date': (self.inst2.due_date + timedelta(days=5)).isoformat(),
                'reason': 'Hacker attempt'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_and_reschedule_via_api(self):
        session = self.client.session
        session['glory_role'] = 'admin'
        session['glory_user_name'] = 'Admin User'
        session.save()

        new_due = self.inst2.due_date + timedelta(days=7)
        response = self.client.post(
            f"/api/orders/{self.order.id}/installments/{self.inst2.id}/reschedule/",
            data=json.dumps({
                'new_due_date': new_due.isoformat(),
                'reason': 'Official authorized reschedule via REST API',
                'notify_customer': True
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.inst2.refresh_from_db()
        self.assertEqual(self.inst2.due_date, new_due)


class FullPaymentBackwardCompatibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.order = InstallmentService.create_order_with_installments({
            'customer_name': 'Full Payment Customer',
            'email': 'fullpay@test.com',
            'phone': '+919123456789',
            'total_amount': Decimal('45000.00'),
            'payment_plan': 'FULL_PAYMENT'
        })

    def test_full_payment_order_flow(self):
        self.assertEqual(self.order.payment_plan, 'FULL_PAYMENT')
        self.assertEqual(self.order.payment_status, 'PENDING_PAYMENT')
        self.assertEqual(self.order.remaining_amount, Decimal('45000.00'))
        self.assertEqual(self.order.installments.count(), 0)

        success, txn, msg = PaymentService.process_payment(
            order=self.order,
            installment_id=None,
            amount=Decimal('45000.00'),
            gateway='UPI',
            gateway_payment_id='PAY-FULL-001',
            idempotency_key='IDEMP-FULL-001'
        )
        self.assertTrue(success)
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid_amount, Decimal('45000.00'))
        self.assertEqual(self.order.remaining_amount, Decimal('0.00'))
        self.assertEqual(self.order.payment_status, 'FULLY_PAID')
