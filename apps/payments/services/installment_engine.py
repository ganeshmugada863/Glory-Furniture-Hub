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
    def apply_plan_to_order(cls, order, plan, start_date=None, total_days=None):
        """
        Atomically snapshots an InstallmentPlan onto an Order and generates
        individual Installment records in the database scheduled matching the product's duration days.
        """
        if start_date is None:
            start_date = timezone.now().date()

        if total_days is None:
            if order.product and hasattr(order.product, 'installment_days') and order.product.installment_days is not None:
                total_days = order.product.installment_days
            elif plan and hasattr(plan, 'interval_days') and hasattr(plan, 'installment_count'):
                total_days = plan.interval_days * (plan.installment_count - 1) if plan.installment_count > 1 else 60
            else:
                total_days = 60

        total_days = max(1, int(total_days))
        day2_offset = min(total_days, max(0, int(round(total_days / 2.0))))
        day3_offset = total_days

        raw_schedule = cls.calculate_schedule(total_amount=order.total_amount, count=3)
        amounts = [item['amount'] for item in raw_schedule]
        dates = [
            start_date,
            start_date + timedelta(days=day2_offset),
            start_date + timedelta(days=day3_offset),
        ]
        labels = [
            'Payment 1 of 3 (Checkout)',
            f'Payment 2 of 3 (Day {day2_offset})',
            f'Payment 3 of 3 (Day {day3_offset} Completion)',
        ]

        with transaction.atomic():
            # Clear any existing non-paid installments for fresh assignment
            order.installments.exclude(status='PAID').delete()

            snapshot_items = []
            for num, (amt, due, lbl) in enumerate(zip(amounts, dates, labels), start=1):
                inst, created = Installment.objects.get_or_create(
                    order=order,
                    installment_number=num,
                    defaults={
                        'amount': amt,
                        'due_date': due,
                        'status': 'PENDING'
                    }
                )
                if not created and inst.status != 'PAID':
                    inst.amount = amt
                    inst.due_date = due
                    inst.save()

                snapshot_items.append({
                    'number': num,
                    'amount': str(amt),
                    'due_date': str(due),
                    'label': lbl
                })

            plan_name_text = f"3 Equal Installments ({total_days} Days)"
            order.payment_type = 'INSTALLMENT'
            order.plan_name = plan_name_text
            order.payment_plan = 'PLAN_3'
            order.installment_plan_snapshot = {
                'plan_id': plan.id if plan else None,
                'plan_name': plan_name_text,
                'installment_count': 3,
                'total_days': total_days,
                'duration_days': total_days,
                'schedule': snapshot_items,
                'snapshot_timestamp': str(timezone.now())
            }

            first_unpaid = order.installments.filter(status='PENDING').order_by('installment_number').first()
            order.next_due_date = first_unpaid.due_date if first_unpaid else None
            order.save()

        return [
            {'number': num, 'amount': amt, 'due_date': due, 'label': lbl}
            for num, (amt, due, lbl) in enumerate(zip(amounts, dates, labels), start=1)
        ]

    @classmethod
    def get_three_equal_installments_plan(cls):
        """Returns or creates the single standard 3 Equal Installments plan matching Image 1."""
        cls.ensure_default_plans()
        plan = InstallmentPlan.objects.filter(
            slug__in=['3-monthly-payments', 'three-equal-installments'],
            is_active=True
        ).first()
        if not plan:
            plan = InstallmentPlan.objects.filter(installment_count=3, is_active=True).first()
        return plan

    @classmethod
    def get_three_equal_installments_schedule(cls, total_amount, start_date=None, total_days=None):
        """
        Generates the exact 3-equal-parts schedule matching product days:
        - Installment 1: Due Today | 'Pay now to confirm your order'
        - Installment 2: Due in {day2_offset} days | 'Pay on the scheduled date'
        - Installment 3: Due in {day3_offset} days | 'Pay on the scheduled date'
        Strict Decimal precision: sum(installments) == total_amount with remainder in part 3.
        """
        if start_date is None:
            start_date = timezone.now().date()

        days = max(1, int(total_days)) if total_days is not None else 60
        day2_offset = min(days, max(0, int(round(days / 2.0))))
        day3_offset = days

        raw_schedule = cls.calculate_schedule(total_amount=total_amount, count=3)
        amounts = [item['amount'] for item in raw_schedule]

        milestones = [
            {
                'number': 1,
                'label': 'Installment 1',
                'subtext': 'Pay now to confirm your order',
                'due_text': 'Due Today',
                'amount': amounts[0],
                'due_date': start_date,
                'days_offset': 0,
            },
            {
                'number': 2,
                'label': 'Installment 2',
                'subtext': 'Pay on the scheduled date',
                'due_text': f'Due in {day2_offset} days',
                'amount': amounts[1],
                'due_date': start_date + timedelta(days=day2_offset),
                'days_offset': day2_offset,
            },
            {
                'number': 3,
                'label': 'Installment 3',
                'subtext': 'Pay on the scheduled date',
                'due_text': f'Due in {day3_offset} days',
                'amount': amounts[2],
                'due_date': start_date + timedelta(days=day3_offset),
                'days_offset': day3_offset,
            }
        ]
        return milestones

    @classmethod
    def get_active_plans_for_amount(cls, amount):
        """
        Returns active InstallmentPlans eligible for the specified order total.
        Image 1 specifies the single 3 Equal Installments option.
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
        """
        Seeds standard plans: Full Payment and 3 Equal Installments (Image 1).
        Deactivates and removes multi-stage plans (2-installments, 6-easy-installments) from Image 2.
        """
        # Deactivate / remove Image 2 multi-contract plans
        InstallmentPlan.objects.filter(slug__in=['2-installments', '6-easy-installments']).update(is_active=False)

        # Full Payment plan
        full_plan, created = InstallmentPlan.objects.get_or_create(
            slug='full-payment',
            defaults={
                'name': 'Full Payment (100% Upfront)',
                'installment_count': 1,
                'percentages': [100],
                'interval_days': 0,
                'min_amount': Decimal('0.00'),
                'is_active': True,
                'display_order': 1,
                'description': 'Pay complete amount now with instant booking confirmation.'
            }
        )
        if not created and not full_plan.is_active:
            full_plan.is_active = True
            full_plan.save()

        # 3 Equal Installments plan (Image 1)
        plan_3, created = InstallmentPlan.objects.get_or_create(
            slug='3-monthly-payments',
            defaults={
                'name': '3 Equal Installments',
                'installment_count': 3,
                'percentages': [],
                'interval_days': 30,
                'min_amount': Decimal('0.00'),
                'is_active': True,
                'display_order': 2,
                'description': 'Split the total cost into 3 equal parts. Pay the first installment now and the remaining 2 installments later as per schedule.'
            }
        )
        if not created:
            plan_3.name = '3 Equal Installments'
            plan_3.description = 'Split the total cost into 3 equal parts. Pay the first installment now and the remaining 2 installments later as per schedule.'
            plan_3.is_active = True
            plan_3.min_amount = Decimal('0.00')
            plan_3.display_order = 2
            plan_3.save()
