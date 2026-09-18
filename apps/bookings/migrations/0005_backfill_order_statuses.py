from django.db import migrations
from decimal import Decimal


def backfill_order_statuses(apps, schema_editor):
    Order = apps.get_model('bookings', 'Order')
    OrderStatusHistory = apps.get_model('bookings', 'OrderStatusHistory')

    for order in Order.objects.all():
        # 1. Determine verified paid amount from modern payments or legacy transactions
        paid_from_payments = sum(
            (p.amount for p in order.payments.filter(status='PAID')),
            Decimal('0.00')
        )
        paid_from_legacy = sum(
            (t.amount for t in order.transactions.filter(status='SUCCESS')),
            Decimal('0.00')
        )
        total_verified = paid_from_payments or paid_from_legacy or (order.paid_amount or Decimal('0.00'))

        order.paid_amount = min(order.total_amount, total_verified)
        order.remaining_amount = max(Decimal('0.00'), order.total_amount - order.paid_amount)

        # 2. Determine payment_status
        if order.paid_amount >= order.total_amount and order.total_amount > Decimal('0.00'):
            order.payment_status = 'FULLY_PAID'
        elif order.paid_amount > Decimal('0.00'):
            order.payment_status = 'PARTIALLY_PAID'
        elif order.order_status == 'FULLY_PAID':
            order.payment_status = 'FULLY_PAID'
        elif order.order_status == 'PARTIALLY_PAID':
            order.payment_status = 'PARTIALLY_PAID'
        else:
            order.payment_status = 'PENDING'

        # 3. Determine fulfillment_status from historical order_status
        old_status = (order.order_status or '').upper()
        if old_status == 'DELIVERED':
            order.fulfillment_status = 'DELIVERED'
        elif old_status == 'SHIPPED':
            order.fulfillment_status = 'SHIPPED'
        elif old_status in ['IN_PRODUCTION', 'PROCESSING']:
            order.fulfillment_status = 'IN_PRODUCTION'
        else:
            order.fulfillment_status = 'CONFIRMED'

        order.save(update_fields=['paid_amount', 'remaining_amount', 'payment_status', 'fulfillment_status'])

        # 4. Create initial status history entry
        OrderStatusHistory.objects.get_or_create(
            order=order,
            fulfillment_status=order.fulfillment_status,
            defaults={
                'previous_status': 'ORDER_PLACED',
                'admin_notes': 'Initial historical status migration backfill.'
            }
        )


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_order_fulfillment_status_order_payment_status_and_more'),
        ('payments', '0002_payment_admin_notes_payment_is_manual_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_order_statuses, reverse_backfill),
    ]
