import json
import base64
import hmac
import hashlib
from decimal import Decimal
from datetime import timedelta

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from apps.store.models import Category, Product
from apps.bookings.models import Order, Installment, Booking
from apps.payments.models import InstallmentPlan, Payment, WebhookEvent
from apps.payments.services import InstallmentEngine, CashfreeService, WebhookService


class InstallmentEngineTests(TestCase):
    """Verifies that multi-installment calculations strictly maintain sum equality with Decimal."""

    def test_three_installments_sum_equality_even_amount(self):
        total = Decimal('100000.00')
        schedule = InstallmentEngine.calculate_schedule(total, count=3)
        self.assertEqual(len(schedule), 3)
        self.assertEqual(schedule[0]['amount'], Decimal('33333.33'))
        self.assertEqual(schedule[1]['amount'], Decimal('33333.33'))
        self.assertEqual(schedule[2]['amount'], Decimal('33333.34'))

        # Sum must strictly equal total amount
        calculated_sum = sum(item['amount'] for item in schedule)
        self.assertEqual(calculated_sum, total)

    def test_three_installments_sum_equality_odd_amount(self):
        total = Decimal('99999.99')
        schedule = InstallmentEngine.calculate_schedule(total, count=3)
        calculated_sum = sum(item['amount'] for item in schedule)
        self.assertEqual(calculated_sum, total)

    def test_two_installments_50_50(self):
        total = Decimal('45555.55')
        schedule = InstallmentEngine.calculate_schedule(total, count=2, percentages=[50, 50])
        calculated_sum = sum(item['amount'] for item in schedule)
        self.assertEqual(calculated_sum, total)

    def test_six_installments(self):
        total = Decimal('150000.00')
        schedule = InstallmentEngine.calculate_schedule(total, count=6)
        self.assertEqual(len(schedule), 6)
        calculated_sum = sum(item['amount'] for item in schedule)
        self.assertEqual(calculated_sum, total)

    def test_snapshot_preservation(self):
        """Modifying a global plan later must NOT alter an existing order's schedule."""
        cat = Category.objects.create(name='Cots', slug='cots')
        prod = Product.objects.create(name='Teak Cot', category=cat, price=Decimal('60000.00'))
        order = Order.objects.create(
            order_number='ORD-TEST-001',
            customer_name='John Doe',
            email='john@example.com',
            phone='9876543210',
            product=prod,
            product_name=prod.name,
            unit_price=Decimal('60000.00'),
            total_amount=Decimal('60000.00'),
            remaining_amount=Decimal('60000.00')
        )

        plan = InstallmentPlan.objects.create(
            name='3 Installments Test',
            slug='3-test',
            installment_count=3,
            interval_days=30
        )

        InstallmentEngine.apply_plan_to_order(order, plan)
        self.assertEqual(order.installments.count(), 3)
        self.assertEqual(order.installments.first().amount, Decimal('20000.00'))

        # Now admin changes global plan to 4 installments
        plan.installment_count = 4
        plan.save()

        # Order must retain its 3-installment snapshot!
        order.refresh_from_db()
        self.assertEqual(order.installments.count(), 3)
        self.assertEqual(order.installment_plan_snapshot['installment_count'], 3)


class CashfreeServiceTests(TestCase):
    """Verifies Cashfree order payload construction and phone number sanitization."""

    def test_phone_sanitization(self):
        self.assertEqual(CashfreeService.sanitize_phone('+91 98765 43210'), '9876543210')
        self.assertEqual(CashfreeService.sanitize_phone('919876543210'), '9876543210')
        self.assertEqual(CashfreeService.sanitize_phone('09876543210'), '9876543210')
        self.assertEqual(CashfreeService.sanitize_phone(''), '9876543210')

    def test_create_order_simulation_mode(self):
        cat = Category.objects.create(name='Tables', slug='tables')
        prod = Product.objects.create(name='Teak Table', category=cat, price=Decimal('25000.00'))
        order = Order.objects.create(
            order_number='ORD-TEST-CF1',
            customer_name='Alice Smith',
            email='alice@example.com',
            phone='9123456780',
            product=prod,
            product_name=prod.name,
            unit_price=Decimal('25000.00'),
            total_amount=Decimal('25000.00'),
            remaining_amount=Decimal('25000.00')
        )

        res = CashfreeService.create_order(order)
        self.assertIn('order_id', res)
        self.assertIn('payment_session_id', res)
        self.assertEqual(res['order_amount'], 25000.0)


class WebhookServiceTests(TestCase):
    """Verifies HMAC signature verification, idempotency, and atomic database state updates."""

    def setUp(self):
        self.secret = 'test_cashfree_secret_key_12345'
        self.patch_settings = self.settings(CASHFREE_CLIENT_SECRET=self.secret)
        self.patch_settings.enable()

        self.cat = Category.objects.create(name='Chairs', slug='chairs')
        self.prod = Product.objects.create(name='Royal Teak Chair', category=self.cat, price=Decimal('30000.00'))
        self.order = Order.objects.create(
            order_number='ORD-TEST-WH1',
            customer_name='Bob Patron',
            email='bob@example.com',
            phone='9988776655',
            product=self.prod,
            product_name=self.prod.name,
            unit_price=Decimal('30000.00'),
            total_amount=Decimal('30000.00'),
            remaining_amount=Decimal('30000.00')
        )

    def tearDown(self):
        self.patch_settings.disable()

    def test_webhook_signature_verification_valid_and_invalid(self):
        body = b'{"data":{"order":{"order_id":"CF_ORD_TEST"}}}'
        timestamp = '1726400000'

        # Compute valid signature
        sig_data = f"{timestamp}{body.decode('utf-8')}"
        mac = hmac.new(self.secret.encode('utf-8'), sig_data.encode('utf-8'), hashlib.sha256).digest()
        valid_sig = base64.b64encode(mac).decode('utf-8')

        # Valid must pass
        self.assertTrue(WebhookService.verify_signature(body, timestamp, valid_sig))

        # Invalid must fail
        self.assertFalse(WebhookService.verify_signature(body, timestamp, 'invalid_signature_xyz'))

    def test_webhook_atomic_payment_success(self):
        cf_order_id = f"CF_ORD_{self.order.id}_ABC123"
        payload = {
            "type": "PAYMENT_SUCCESS_WEBHOOK",
            "event_time": "2026-09-15T19:00:00Z",
            "data": {
                "order": {
                    "order_id": cf_order_id,
                    "order_amount": 30000.0
                },
                "payment": {
                    "cf_payment_id": "CF_PAY_998877",
                    "payment_status": "SUCCESS",
                    "payment_amount": 30000.0,
                    "payment_method": {"upi": {"channel": "intent"}}
                }
            }
        }
        body_bytes = json.dumps(payload).encode('utf-8')
        timestamp = '1726400000'

        sig_data = f"{timestamp}{body_bytes.decode('utf-8')}"
        mac = hmac.new(self.secret.encode('utf-8'), sig_data.encode('utf-8'), hashlib.sha256).digest()
        signature = base64.b64encode(mac).decode('utf-8')

        headers = {
            'X-Webhook-Timestamp': timestamp,
            'X-Webhook-Signature': signature
        }

        result = WebhookService.process_webhook(body_bytes, headers)
        self.assertEqual(result['status'], 'success')

        # Check Order status updated to FULLY_PAID
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'FULLY_PAID')
        self.assertEqual(self.order.paid_amount, Decimal('30000.00'))
        self.assertEqual(self.order.remaining_amount, Decimal('0.00'))

        # Check Payment record created and marked PAID
        payment = Payment.objects.filter(gateway_order_id=cf_order_id).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'PAID')
        self.assertEqual(payment.gateway_payment_id, 'CF_PAY_998877')

    def test_webhook_idempotency_duplicate_event(self):
        """Sending the same webhook payload twice must NOT double credit the payment."""
        cf_order_id = f"CF_ORD_{self.order.id}_IDEMP1"
        payload = {
            "type": "PAYMENT_SUCCESS_WEBHOOK",
            "data": {
                "order": {"order_id": cf_order_id, "order_amount": 30000.0},
                "payment": {"cf_payment_id": "CF_PAY_IDEMP_01", "payment_status": "SUCCESS", "payment_amount": 30000.0}
            }
        }
        body_bytes = json.dumps(payload).encode('utf-8')
        timestamp = '1726400000'
        sig_data = f"{timestamp}{body_bytes.decode('utf-8')}"
        mac = hmac.new(self.secret.encode('utf-8'), sig_data.encode('utf-8'), hashlib.sha256).digest()
        headers = {
            'X-Webhook-Timestamp': timestamp,
            'X-Webhook-Signature': base64.b64encode(mac).decode('utf-8')
        }

        # First call: succeeds
        res1 = WebhookService.process_webhook(body_bytes, headers)
        self.assertEqual(res1['status'], 'success')

        # Second call with identical payload: returns already_processed
        res2 = WebhookService.process_webhook(body_bytes, headers)
        self.assertEqual(res2['status'], 'already_processed')

        # Payments count must strictly be 1
        self.assertEqual(Payment.objects.filter(gateway_order_id=cf_order_id).count(), 1)


class CustomerAccessIsolationTests(TestCase):
    """Verifies that Customer B cannot access Customer A's checkout or receipt."""

    def setUp(self):
        self.user_a = User.objects.create_user(username='usera', email='usera@example.com', password='password123')
        self.user_b = User.objects.create_user(username='userb', email='userb@example.com', password='password123')

        cat = Category.objects.create(name='Sofas', slug='sofas')
        prod = Product.objects.create(name='Teak Royal Sofa', category=cat, price=Decimal('80000.00'))

        self.order_a = Order.objects.create(
            user=self.user_a,
            order_number='ORD-USER-A-01',
            customer_name='User A',
            email='usera@example.com',
            phone='9000011111',
            product=prod,
            product_name=prod.name,
            unit_price=Decimal('80000.00'),
            total_amount=Decimal('80000.00'),
            remaining_amount=Decimal('80000.00')
        )

        self.client_b = Client()
        self.client_b.force_login(self.user_b)

    def test_customer_b_cannot_access_order_a_checkout(self):
        resp = self.client_b.get(f"/payments/checkout/{self.order_a.order_number}/")
        self.assertEqual(resp.status_code, 403)


class ThreeEqualInstallmentsDesignEngineTests(TestCase):
    """
    Verifies that Image 1's 3 Equal Installments UI design and engine are implemented,
    and Image 2's multi-stage plans (2-installments, 6-easy-installments, contracts drawer) are removed.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='patron_image1', email='patron_image1@example.com', password='password123')
        cat = Category.objects.create(name='Dining Suites', slug='dining-suites')
        self.product = Product.objects.create(name='Heritage Teak Set', category=cat, price=Decimal('1000.00'))
        self.order = Order.objects.create(
            user=self.user,
            order_number='ORD-IMG1-1000',
            customer_name='Patron One',
            email='patron_image1@example.com',
            phone='9876543210',
            product=self.product,
            product_name=self.product.name,
            unit_price=Decimal('1000.00'),
            total_amount=Decimal('1000.00'),
            remaining_amount=Decimal('1000.00')
        )
        self.client = Client()
        self.client.force_login(self.user)

    def test_three_equal_installments_schedule_matching_image_1(self):
        """Schedule matches Image 1: 3 parts, Due Today, Due in 30 days, Due in 60 days, exact Decimal precision."""
        schedule = InstallmentEngine.get_three_equal_installments_schedule(self.order.total_amount)
        self.assertEqual(len(schedule), 3)

        # Part 1
        self.assertEqual(schedule[0]['number'], 1)
        self.assertEqual(schedule[0]['label'], 'Installment 1')
        self.assertEqual(schedule[0]['subtext'], 'Pay now to confirm your order')
        self.assertEqual(schedule[0]['due_text'], 'Due Today')
        self.assertEqual(schedule[0]['amount'], Decimal('333.33'))

        # Part 2
        self.assertEqual(schedule[1]['number'], 2)
        self.assertEqual(schedule[1]['label'], 'Installment 2')
        self.assertEqual(schedule[1]['subtext'], 'Pay on the scheduled date')
        self.assertEqual(schedule[1]['due_text'], 'Due in 30 days')
        self.assertEqual(schedule[1]['amount'], Decimal('333.33'))

        # Part 3
        self.assertEqual(schedule[2]['number'], 3)
        self.assertEqual(schedule[2]['label'], 'Installment 3')
        self.assertEqual(schedule[2]['subtext'], 'Pay on the scheduled date')
        self.assertEqual(schedule[2]['due_text'], 'Due in 60 days')
        self.assertEqual(schedule[2]['amount'], Decimal('333.34'))

        # Strict sum equality
        self.assertEqual(sum(s['amount'] for s in schedule), Decimal('1000.00'))

    def test_removal_of_image_2_multi_contract_plans(self):
        """Image 2's 2-installments and 6-easy-installments plans are deactivated/not served."""
        # Pre-create image 2 plans
        InstallmentPlan.objects.create(name='2 Parts', slug='2-installments', installment_count=2, is_active=True)
        InstallmentPlan.objects.create(name='6 Parts', slug='6-easy-installments', installment_count=6, is_active=True)

        # Call engine seeding
        InstallmentEngine.ensure_default_plans()

        # Check that 2-installments and 6-easy-installments are deactivated
        self.assertFalse(InstallmentPlan.objects.filter(slug='2-installments', is_active=True).exists())
        self.assertFalse(InstallmentPlan.objects.filter(slug='6-easy-installments', is_active=True).exists())

        # Active plans must only include full-payment and 3-monthly-payments (3 Equal Installments)
        active_plans = InstallmentEngine.get_active_plans_for_amount(Decimal('1000.00'))
        active_slugs = [p.slug for p in active_plans]
        self.assertIn('3-monthly-payments', active_slugs)
        self.assertNotIn('2-installments', active_slugs)
        self.assertNotIn('6-easy-installments', active_slugs)

    def test_checkout_ui_renders_image_1_elements(self):
        """Checkout page contains Image 1's UI elements and does NOT contain Image 2's elements."""
        resp = self.client.get(f"/payments/checkout/{self.order.order_number}/")
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')

        # Assert Image 1 elements are present
        self.assertIn('3 Equal Installments', content)
        self.assertIn('FLEXIBLE', content)
        self.assertIn('Your Installment Plan (3 Equal Parts)', content)
        self.assertIn('Simple &amp; Equal Payments', content)
        self.assertIn('Three equal installments make it easier to bring your dream furniture home.', content)
        self.assertIn('Secure Payment Powered by Cashfree', content)
        self.assertIn('Pay First Installment', content)
        self.assertIn('Installment 1', content)
        self.assertIn('Installment 2', content)
        self.assertIn('Installment 3', content)
        self.assertIn('Due Today', content)
        self.assertIn('Due in 30 days', content)
        self.assertIn('Due in 60 days', content)

        # Assert Image 2 elements are completely removed
        self.assertNotIn('Option B: Multi-Stage Installment Plan', content)
        self.assertNotIn('SELECT AVAILABLE INSTALLMENT CONTRACT:', content)
        self.assertNotIn('6 Easy Installments', content)
        self.assertNotIn('2 Installments (50/50 Split)', content)

