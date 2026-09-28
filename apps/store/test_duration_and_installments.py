import json
from decimal import Decimal
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils import timezone
from apps.store.models import Category, Product
from apps.bookings.models import Order, Installment
from apps.bookings.services import InstallmentService
from apps.payments.services.installment_engine import InstallmentEngine


class ProductDurationAndInstallmentSchedulingTests(TestCase):
    """
    Complete targeted test suite for Product Duration & 3-Installment Scheduling (Tests A - G & Edge Cases).
    """

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='studio_master_admin',
            email='admin@gloryfurniture.com',
            password='AdminPassword123!'
        )
        self.category = Category.objects.create(name='Teak Furniture', slug='teak-furniture')
        self.patron = User.objects.create_user(
            username='patron_user',
            email='patron@glory.com',
            password='PatronPassword123!'
        )
        self.admin_products_url = reverse('admin_products')

    def _login_admin(self):
        self.client.force_login(self.admin_user)
        session = self.client.session
        session['glory_role'] = 'admin'
        session['glory_admin_authenticated'] = True
        session.save()

    def test_A_product_creation_with_duration(self):
        """
        Test A — Product creation:
        Create Product A with Duration = 10 days. Verify the value is persisted.
        """
        self._login_admin()
        response = self.client.post(self.admin_products_url, {
            'action': 'add_product',
            'name': 'Solid Teak Coffee Table',
            'category_id': self.category.id,
            'price': '18000',
            'installment_days': '10',
            'material': 'Grade-A Teak',
            'style': 'Classic',
            'dimensions': '4x2 ft',
            'lead_time': '5-7 Days',
            'in_stock': '1',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        product = Product.objects.filter(name='Solid Teak Coffee Table').first()
        self.assertIsNotNone(product)
        self.assertEqual(product.installment_days, 10)

    def test_B_product_editing_duration(self):
        """
        Test B — Product editing:
        Change 10 -> 30 days. Verify the product now shows 30 days.
        """
        self._login_admin()
        product = Product.objects.create(
            name='Vintage Teak Bookshelf',
            category=self.category,
            price=Decimal('24000.00'),
            installment_days=10
        )
        self.assertEqual(product.installment_days, 10)

        response = self.client.post(self.admin_products_url, {
            'action': 'edit_product',
            'product_id': product.id,
            'name': 'Vintage Teak Bookshelf Updated',
            'category_id': self.category.id,
            'price': '24000',
            'installment_days': '30',
            'material': 'Grade-A Teak',
            'style': 'Classic',
            'dimensions': '6x3 ft',
            'lead_time': '5-7 Days',
            'in_stock': '1',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        product.refresh_from_db()
        self.assertEqual(product.installment_days, 30)

    def test_C_ten_day_installment_order(self):
        """
        Test C — 10-day installment order:
        Create/order a product with Duration = 10 days, 3 Installments.
        Verify all 3 installments are scheduled within the 10-day window:
        Day 0 -> Installment 1
        Day 5 -> Installment 2
        Day 10 -> Installment 3
        """
        product = Product.objects.create(
            name='Royal Teak Bed 10D',
            category=self.category,
            price=Decimal('90000.00'),
            installment_days=10
        )
        start_date = timezone.now().date()
        order = InstallmentService.create_order_with_installments({
            'product': product,
            'customer_name': 'Ramesh Kumar',
            'email': 'ramesh@example.com',
            'phone': '9876543210',
            'total_amount': Decimal('90000.00'),
            'unit_price': Decimal('90000.00'),
            'payment_plan': 'THREE_INSTALLMENTS',
        }, start_date=start_date)

        installments = list(order.installments.all().order_by('installment_number'))
        self.assertEqual(len(installments), 3)

        # Amounts: 30000 each
        self.assertEqual(installments[0].amount, Decimal('30000.00'))
        self.assertEqual(installments[1].amount, Decimal('30000.00'))
        self.assertEqual(installments[2].amount, Decimal('30000.00'))

        # Dates: Day 0, Day 5, Day 10
        self.assertEqual(installments[0].due_date, start_date)
        self.assertEqual(installments[1].due_date, start_date + timedelta(days=5))
        self.assertEqual(installments[2].due_date, start_date + timedelta(days=10))

        # Final installment does not exceed 10 days
        self.assertLessEqual(installments[2].due_date, start_date + timedelta(days=10))

    def test_D_thirty_day_installment_order(self):
        """
        Test D — 30-day installment order:
        Create/order a product with Duration = 30 days, 3 Installments.
        Verify all 3 installments are scheduled within the 30-day window:
        Day 0 -> Installment 1
        Day 15 -> Installment 2
        Day 30 -> Installment 3
        """
        product = Product.objects.create(
            name='Burma Teak Sofa 30D',
            category=self.category,
            price=Decimal('60000.00'),
            installment_days=30
        )
        start_date = timezone.now().date()
        order = InstallmentService.create_order_with_installments({
            'product': product,
            'customer_name': 'Pooja Verma',
            'email': 'pooja@example.com',
            'phone': '9876543211',
            'total_amount': Decimal('60000.00'),
            'unit_price': Decimal('60000.00'),
            'payment_plan': 'THREE_INSTALLMENTS',
        }, start_date=start_date)

        installments = list(order.installments.all().order_by('installment_number'))
        self.assertEqual(len(installments), 3)

        # Amounts: 20000 each
        self.assertEqual(installments[0].amount, Decimal('20000.00'))
        self.assertEqual(installments[1].amount, Decimal('20000.00'))
        self.assertEqual(installments[2].amount, Decimal('20000.00'))

        # Dates: Day 0, Day 15, Day 30
        self.assertEqual(installments[0].due_date, start_date)
        self.assertEqual(installments[1].due_date, start_date + timedelta(days=15))
        self.assertEqual(installments[2].due_date, start_date + timedelta(days=30))

        # Final installment does not exceed 30 days
        self.assertLessEqual(installments[2].due_date, start_date + timedelta(days=30))

    def test_E_different_products_generate_own_schedules(self):
        """
        Test E — Different products:
        Product A = 10 days, Product B = 30 days, Product C = 60 days, Product D = 90 days.
        Verify each product generates its own schedule.
        """
        start_date = timezone.now().date()
        durations = [10, 30, 60, 90]
        for d in durations:
            prod = Product.objects.create(
                name=f'Product with {d} days',
                category=self.category,
                price=Decimal('30000.00'),
                installment_days=d
            )
            dates = InstallmentService.get_schedule_dates(start_date, total_days=prod.installment_days)
            self.assertEqual(dates[0], start_date)
            self.assertEqual(dates[1], start_date + timedelta(days=round(d / 2)))
            self.assertEqual(dates[2], start_date + timedelta(days=d))
            self.assertLessEqual(dates[2], start_date + timedelta(days=d))

    def test_F_historical_order_protection(self):
        """
        Test F — Historical order protection:
        Day 1: Customer orders product when duration is 30 days.
        Day 5: Admin changes product duration: 30 -> 60 days.
        Verify the existing customer/order retains its original 30-day schedule.
        """
        product = Product.objects.create(
            name='Handcarved Dining Suite',
            category=self.category,
            price=Decimal('75000.00'),
            installment_days=30
        )
        start_date = timezone.now().date()
        order = InstallmentService.create_order_with_installments({
            'product': product,
            'customer_name': 'Vikramaditya',
            'email': 'vikram@example.com',
            'phone': '9876543212',
            'total_amount': Decimal('75000.00'),
            'unit_price': Decimal('75000.00'),
            'payment_plan': 'THREE_INSTALLMENTS',
        }, start_date=start_date)

        # Capture original dates
        original_dates = [inst.due_date for inst in order.installments.all().order_by('installment_number')]
        self.assertEqual(original_dates[2], start_date + timedelta(days=30))

        # Admin changes product duration to 60 days
        self._login_admin()
        self.client.post(self.admin_products_url, {
            'action': 'edit_product',
            'product_id': product.id,
            'installment_days': '60',
            'name': product.name,
            'category_id': self.category.id,
            'price': '75000',
        })
        product.refresh_from_db()
        self.assertEqual(product.installment_days, 60)

        # Historical order MUST STILL HAVE original 30-day dates
        order.refresh_from_db()
        persisted_dates = [inst.due_date for inst in order.installments.all().order_by('installment_number')]
        self.assertEqual(persisted_dates, original_dates)
        self.assertEqual(persisted_dates[2], start_date + timedelta(days=30))

    def test_G_invalid_values_rejected(self):
        """
        Test G — Invalid values:
        0, -1, -100, abc, blank, 10.5 must be rejected with 'Please enter a valid positive number of days.'
        """
        self._login_admin()
        invalid_inputs = ['0', '-1', '-100', 'abc', '', '10.5', '  ']
        for invalid_val in invalid_inputs:
            # Test in add_product
            initial_count = Product.objects.count()
            response = self.client.post(self.admin_products_url, {
                'action': 'add_product',
                'name': f'Invalid Product {invalid_val}',
                'category_id': self.category.id,
                'price': '10000',
                'installment_days': invalid_val,
            }, follow=True)
            self.assertEqual(Product.objects.count(), initial_count, f"Product should not be created for duration: {invalid_val}")
            messages = [m.message for m in get_messages(response.wsgi_request)]
            self.assertTrue(
                any("Please enter a valid positive number of days." in m for m in messages),
                f"Validation error missing for invalid input: {invalid_val}"
            )

    def test_edge_case_durations(self):
        """
        Test edge cases (Section 19):
        1, 2, 3, 5, 7, 10, 15, 30, 45, 60, 90, 365 days.
        Ensure calculation never crashes and final installment NEVER exceeds product duration.
        """
        start_date = timezone.now().date()
        test_durations = [1, 2, 3, 5, 7, 10, 15, 30, 45, 60, 90, 365]

        for d in test_durations:
            dates = InstallmentService.get_schedule_dates(start_date, total_days=d)
            self.assertEqual(len(dates), 3, f"Must always produce 3 dates for duration {d}")

            # Installment 1 is start_date (Day 0)
            self.assertEqual(dates[0], start_date)

            # Installment 2 is within window
            self.assertGreaterEqual(dates[1], dates[0])
            self.assertLessEqual(dates[1], dates[2])

            # Installment 3 NEVER exceeds start_date + d days
            max_allowed = start_date + timedelta(days=d)
            self.assertLessEqual(dates[2], max_allowed, f"Final installment {dates[2]} exceeded max allowed {max_allowed} for duration {d}")

            # For d >= 2, all 3 dates should be distinct and strictly increasing
            if d >= 2:
                self.assertLess(dates[0], dates[1], f"Date 0 must be < Date 1 for duration {d}")
                self.assertLess(dates[1], dates[2], f"Date 1 must be < Date 2 for duration {d}")
                self.assertEqual(dates[2], max_allowed)

    def test_checkout_displays_exact_product_duration_dates(self):
        """
        Verify that on the checkout page, the 3 installment cards dynamically display
        the exact product-duration dates:
        - 10 days product -> Due Today, Due in 5 days, Due in 10 days
        - 20 days product -> Due Today, Due in 10 days, Due in 20 days
        - 30 days product -> Due Today, Due in 15 days, Due in 30 days
        """
        self.client.force_login(self.patron)

        for duration, day2, day3 in [(10, 5, 10), (20, 10, 20), (30, 15, 30)]:
            prod = Product.objects.create(
                name=f'Custom Teak {duration}D',
                category=self.category,
                price=Decimal('10.00'),
                installment_days=duration
            )
            order = Order.objects.create(
                user=self.patron,
                customer_name='Patron Test',
                email='patron@glory.com',
                phone='9876543210',
                product=prod,
                product_name=prod.name,
                unit_price=Decimal('10.00'),
                total_amount=Decimal('10.00'),
                remaining_amount=Decimal('10.00'),
                payment_plan='FULL_PAYMENT'
            )
            url = reverse('payment_checkout', kwargs={'order_number': order.order_number})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            content = response.content.decode('utf-8')

            # Verify the exact due texts are present
            self.assertIn('Due Today', content)
            self.assertIn(f'Due in {day2} days', content)
            self.assertIn(f'Due in {day3} days', content)
            self.assertIn(f'Scheduled Over {duration} Days', content)
            self.assertIn(f'across {duration} days', content)

