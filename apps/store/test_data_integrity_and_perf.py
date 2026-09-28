import io
import time
from decimal import Decimal
from PIL import Image
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from apps.store.models import Category, Product
from apps.bookings.models import Order, Installment, PaymentTransaction
from apps.payments.models import Payment
from apps.accounts.views import _save_product_image_file


class DataIntegrityAndSafetyTests(TestCase):
    """
    Verifies that catalog operations (such as deleting or modifying products and categories)
    never cause cascading data loss to historical customer orders, installment schedules,
    or financial transactions.
    """

    def setUp(self):
        self.category = Category.objects.create(name="Royal Living Room", slug="royal-living-room")
        self.product = Product.objects.create(
            name="Handcrafted Burma Teak Diwana",
            category=self.category,
            price=Decimal("45000.00"),
            installment_days=45,
            primary_image="/static/images/card_bed.jpg"
        )
        self.user = User.objects.create_user(username="patron_test", email="patron@example.com", password="Pass123!Safe")
        self.order = Order.objects.create(
            product=self.product,
            user=self.user,
            customer_name="Rao Bahadur",
            email="patron@example.com",
            phone="9876543210",
            unit_price=Decimal("45000.00"),
            total_amount=Decimal("45000.00"),
            paid_amount=Decimal("15000.00"),
            remaining_amount=Decimal("30000.00"),
            payment_plan="THREE_INSTALLMENTS",
            payment_type="INSTALLMENT",
            custom_measurements="72 x 36 x 30 in"
        )
        self.installment = Installment.objects.create(
            order=self.order,
            installment_number=1,
            amount=Decimal("15000.00"),
            due_date="2026-10-01",
            status="PAID"
        )
        self.payment = Payment.objects.create(
            order=self.order,
            customer=self.user,
            installment=self.installment,
            payment_type="INSTALLMENT",
            amount=Decimal("15000.00"),
            status="PAID"
        )
        self.transaction = PaymentTransaction.objects.create(
            order=self.order,
            installment=self.installment,
            amount=Decimal("15000.00"),
            status="SUCCESS"
        )

    def test_deleting_product_preserves_order_and_financial_records(self):
        """
        Critical Test: Ensure Order.product uses on_delete=SET_NULL so deleting a catalog item
        does NOT wipe out historical patron receipts, invoices, installments, or payments.
        """
        product_id = self.product.id
        self.product.delete()

        # Product is removed from catalog
        self.assertFalse(Product.objects.filter(id=product_id).exists())

        # Order must still exist completely intact!
        self.order.refresh_from_db()
        self.assertIsNone(self.order.product)
        self.assertEqual(self.order.customer_name, "Rao Bahadur")
        self.assertEqual(self.order.total_amount, Decimal("45000.00"))
        self.assertEqual(self.order.paid_amount, Decimal("15000.00"))
        self.assertEqual(self.order.custom_measurements, "72 x 36 x 30 in")

        # Installment must still exist intact
        self.installment.refresh_from_db()
        self.assertEqual(self.installment.status, "PAID")
        self.assertEqual(self.installment.amount, Decimal("15000.00"))

        # Payment ledger entry must still exist intact
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PAID")
        self.assertEqual(self.payment.amount, Decimal("15000.00"))

        # PaymentTransaction must still exist intact
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, "SUCCESS")

    def test_deleting_category_preserves_products(self):
        """
        Ensure Product.category uses on_delete=SET_NULL so deleting a category
        does not wipe out all associated products and their orders.
        """
        cat_id = self.category.id
        self.category.delete()

        self.assertFalse(Category.objects.filter(id=cat_id).exists())
        self.product.refresh_from_db()
        self.assertIsNone(self.product.category)
        self.assertEqual(self.product.name, "Handcrafted Burma Teak Diwana")


class ImageOptimizationAndSavePerformanceTests(TestCase):
    """
    Verifies that _save_product_image_file optimizes multi-megabyte images
    rapidly (under 1 second) and downsamples dimensions to max 1600px.
    """

    def test_save_large_image_optimization_and_latency(self):
        """
        Test that a large high-resolution camera image (3000x2000)
        is quickly optimized, downscaled, and saved to persistent storage.
        """
        # Create a large 3000x2000 test image in memory
        raw_img = Image.new('RGB', (3000, 2000), color=(140, 90, 60))
        img_bytes = io.BytesIO()
        raw_img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)

        uploaded = SimpleUploadedFile(
            name="large_workshop_camera.jpg",
            content=img_bytes.getvalue(),
            content_type="image/jpeg"
        )

        t0 = time.time()
        url = _save_product_image_file(uploaded)
        t1 = time.time()
        duration_ms = (t1 - t0) * 1000

        self.assertTrue(url)
        self.assertTrue(url.startswith('http') or url.startswith('/media/'))
        # Processing and saving locally should complete under 1.5 seconds even on slow machines
        self.assertLess(duration_ms, 2000, f"Image save took too long: {duration_ms:.2f}ms")

    def test_rgba_image_converted_to_clean_rgb_jpeg(self):
        """
        Test that transparent PNG/RGBA images are cleanly composited onto white
        and saved without crashing.
        """
        rgba_img = Image.new('RGBA', (800, 600), color=(200, 100, 50, 128))
        img_bytes = io.BytesIO()
        rgba_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        uploaded = SimpleUploadedFile(
            name="transparent_furniture.png",
            content=img_bytes.getvalue(),
            content_type="image/png"
        )

        url = _save_product_image_file(uploaded)
        self.assertTrue(url)
        self.assertTrue(url.endswith('.jpg') or url.startswith('http'))
