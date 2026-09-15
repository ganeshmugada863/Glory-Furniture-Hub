from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from apps.payments.models import InstallmentPlan
from apps.bookings.models import Installment


class InstallmentEngineError(Exception):
    pass


class InstallmentEngine:
    """
    Precision engine for multi-part installment calculations using Decimal.
    Strictly guarantees: SUM(installments) == total_amount.
    Any fraction or rounding difference is automatically absorbed into the final installment.
    """

    @classmethod
    def calculate_schedule(cls, total_amount, count=3, percentages=None, interval_days=30, start_date=None):
        """
        Calculates exact Decimal schedule for any number of installments.
        Guarantees: sum(installments) == total_amount.
        Never uses floating-point arithmetic.
        """
        try:
            total_dec = Decimal(str(total_amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception as e:
            raise InstallmentEngineError(f"Invalid total amount: {total_amount}") from e

        if total_dec <= Decimal('0.00'):
            raise InstallmentEngineError("Order total must be positive.")

        if count < 1:
            raise InstallmentEngineError("Installment count must be at least 1.")

        if count == 1:
            if start_date is None:
                start_date = timezone.now().date()
            return [{
                'number': 1,
                'amount': total_dec,
                'due_date': start_date,
                'label': 'Full Payment'
            }]

        if start_date is None:
            start_date = timezone.now().date()

        amounts = []
        if percentages and len(percentages) == count:
            # Custom percentage distribution
            running_sum = Decimal('0.00')
            for i in range(count - 1):
                pct = Decimal(str(percentages[i]))
                part = (total_dec * pct / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                amounts.append(part)
                running_sum += part
            # Final installment absorbs the remainder
            final_part = total_dec - running_sum
            amounts.append(final_part)
        else:
            # Equal division with remainder absorbed into the final installment
            base_part = (total_dec / Decimal(count)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            running_sum = Decimal('0.00')
            for i in range(count - 1):
                amounts.append(base_part)
                running_sum += base_part
            final_part = total_dec - running_sum
            amounts.append(final_part)

        # Build schedule list with due dates
        schedule = []
        for index, amt in enumerate(amounts, start=1):
            due_date = start_date + timedelta(days=interval_days * (index - 1))
            schedule.append({
                'number': index,
                'amount': amt,
                'due_date': due_date,
                'label': f"Payment {index} of {count}"
            })

        return schedule

    @classmethod
    def apply_plan_to_order(cls, order, plan, start_date=None):
        """
        Atomically snapshots an InstallmentPlan onto an Order and generates
        individual Installment records in the database.
        
        Guarantees:
        - If admin later modifies global plans, this order's snapshot remains immutable.
        """
        if start_date is None:
            start_date = timezone.now().date()

        schedule = cls.calculate_schedule(
            total_amount=order.total_amount,
            count=plan.installment_count,
            percentages=plan.percentages,
            interval_days=plan.interval_days,
            start_date=start_date
        )

        with transaction.atomic():
            # Clear any existing non-paid installments for fresh assignment
            order.installments.exclude(status='PAID').delete()

            snapshot_items = []
            for item in schedule:
                inst, created = Installment.objects.get_or_create(
                    order=order,
                    installment_number=item['number'],
                    defaults={
                        'amount': item['amount'],
                        'due_date': item['due_date'],
                        'status': 'PENDING'
                    }
                )
                if not created and inst.status != 'PAID':
                    inst.amount = item['amount']
                    inst.due_date = item['due_date']
                    inst.save()

                snapshot_items.append({
                    'number': item['number'],
                    'amount': str(item['amount']),
                    'due_date': str(item['due_date']),
                    'label': item['label']
                })

            order.payment_type = 'INSTALLMENT' if plan.installment_count > 1 else 'FULL'
            order.plan_name = plan.name
            order.payment_plan = f"PLAN_{plan.installment_count}"
            order.installment_plan_snapshot = {
                'plan_id': plan.id,
                'plan_name': plan.name,
                'installment_count': plan.installment_count,
                'interval_days': plan.interval_days,
                'schedule': snapshot_items,
                'snapshot_timestamp': str(timezone.now())
            }

            first_unpaid = order.installments.filter(status='PENDING').order_by('installment_number').first()
            order.next_due_date = first_unpaid.due_date if first_unpaid else None
            order.save()

        return schedule

    @classmethod
    def get_active_plans_for_amount(cls, amount):
        """
        Returns active InstallmentPlans eligible for the specified order total.
        If no plans exist in the database, seeds default plans.
        """
        cls.ensure_default_plans()
        amount_dec = Decimal(str(amount))
        plans = InstallmentPlan.objects.filter(is_active=True).order_by('display_order', 'installment_count')
        eligible = []
        for p in plans:
            if p.min_amount and amount_dec < p.min_amount:
                continue
            if p.max_amount and amount_dec > p.max_amount:
                continue
            eligible.append(p)
        return eligible

    @classmethod
    def ensure_default_plans(cls):
        """Seeds standard plans if none exist in the database."""
        if not InstallmentPlan.objects.exists():
            InstallmentPlan.objects.create(
                name='Full Payment (100% Upfront)',
                slug='full-payment',
                installment_count=1,
                percentages=[100],
                interval_days=0,
                min_amount=Decimal('0.00'),
                is_active=True,
                display_order=1,
                description='Pay complete amount now with instant booking confirmation.'
            )
            InstallmentPlan.objects.create(
                name='2 Installments (50/50 Split)',
                slug='2-installments',
                installment_count=2,
                percentages=[50, 50],
                interval_days=30,
                min_amount=Decimal('5000.00'),
                is_active=True,
                display_order=2,
                description='Pay 50% now to initiate handcrafting, and 50% upon workshop completion.'
            )
            InstallmentPlan.objects.create(
                name='3 Monthly Payments',
                slug='3-monthly-payments',
                installment_count=3,
                percentages=[33.33, 33.33, 33.34],
                interval_days=30,
                min_amount=Decimal('10000.00'),
                is_active=True,
                display_order=3,
                description='Convenient 3-stage payments during timber seasoning, joinery, and final buffing.'
            )
            InstallmentPlan.objects.create(
                name='6 Easy Installments',
                slug='6-easy-installments',
                installment_count=6,
                percentages=[],
                interval_days=30,
                min_amount=Decimal('25000.00'),
                is_active=True,
                display_order=4,
                description='Split over 6 monthly installments for bespoke architectural teak suites.'
            )
