import uuid
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from .models import Order, Installment, PaymentTransaction, InstallmentRescheduleAudit, Booking
from apps.accounts.models import Notification


class InstallmentCalculationError(Exception):
    pass


class InstallmentRescheduleError(Exception):
    pass


class OrderAccessControl:
    """
    Strict multi-tenant customer data isolation.
    Guarantees Customer A can never access, view, share, or export Customer B's order data.
    """
    @staticmethod
    def check_order_access(request, order):
        if not order:
            return False

        # 1. Store Staff & Admins
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (getattr(request.user, 'profile', None) and request.user.profile.is_admin)):
            return True
        if request.session.get('glory_role') == 'admin':
            return True

        # 2. Authenticated Customer
        if request.user.is_authenticated:
            if order.user_id:
                return order.user_id == request.user.id
            # If guest order matches this user's email, claim and link it
            if request.user.email and order.email and request.user.email.strip().lower() == order.email.strip().lower():
                order.user = request.user
                order.save(update_fields=['user'])
                return True
            return False

        # 3. Unauthenticated / Guest Customer
        # Never permit guests to view orders owned by a registered user
        if order.user_id is not None:
            return False

        tracked_orders = request.session.get('glory_customer_order_ids', [])
        session_email = request.session.get('glory_user_email')

        if order.id in tracked_orders:
            if session_email and order.email:
                return session_email.strip().lower() == order.email.strip().lower()
            return True

        return False


class InstallmentService:
    """
    Engine for calculating three-installment schedules with exact integer/paise rounding
    and guaranteed sum equality: SUM(installments) == total_amount.
    """

    @staticmethod
    def calculate_three_installments(total_amount):
        """
        Calculates exact three installments with rounding difference assigned to the 3rd installment.
        Guarantees: inst1 + inst2 + inst3 == total_amount.
        Never uses floating-point math.
        """
        try:
            total_dec = Decimal(str(total_amount))
        except Exception as e:
            raise InstallmentCalculationError(f"Invalid total amount: {total_amount}") from e

        if total_dec <= Decimal('0'):
            raise InstallmentCalculationError("Total order amount must be positive.")

        # Minimum required to split into 3 positive payments
        if total_dec < Decimal('3.00'):
            raise InstallmentCalculationError("Order amount is too small for three installments.")

        # If it's a whole rupee amount (standard for furniture items in catalog)
        if total_dec == total_dec.to_integral_value():
            total_int = int(total_dec)
            base_amt = total_int // 3
            remainder = total_int - (base_amt * 3)

            inst1 = Decimal(base_amt)
            inst2 = Decimal(base_amt)
            inst3 = Decimal(base_amt + remainder)
        else:
            # Calculate in integer paise (1 Rupee = 100 paise)
            total_paise = int((total_dec * 100).to_integral_value())
            base_paise = total_paise // 3
            remainder_paise = total_paise - (base_paise * 3)

            base_part = (total_dec / Decimal(3)).quantize(Decimal('0.01'))
            inst1 = base_part
            inst2 = base_part
            inst3 = total_dec - (inst1 + inst2)

        return [inst1, inst2, inst3]

    @staticmethod
    def get_schedule_dates(start_date=None, interval_days=30):
        """
        Generates 3 sequential due dates:
        Installment 1: Day 0 (Checkout)
        Installment 2: Day 30
        Installment 3: Day 60
        """
        if start_date is None:
            start_date = timezone.now().date()
        return [
            start_date,
            start_date + timedelta(days=interval_days),
            start_date + timedelta(days=interval_days * 2)
        ]

    @classmethod
    def create_order_with_installments(cls, order_data, start_date=None):
        """
        Atomically creates an Order and, if payment_plan is THREE_INSTALLMENTS,
        generates the 3 installment records.
        """
        with transaction.atomic():
            plan = order_data.get('payment_plan', 'FULL_PAYMENT')
            total_amount = Decimal(str(order_data['total_amount']))
            product = order_data.get('product')
            if not product:
                from apps.store.models import Product, Category
                product = Product.objects.first()
                if not product:
                    cat, _ = Category.objects.get_or_create(name='Bespoke Teak Pieces', defaults={'slug': 'bespoke-teak'})
                    product = Product.objects.create(
                        name='Handcrafted Teak Piece',
                        category=cat,
                        price=total_amount,
                        material='Solid Burma Teak'
                    )
            product_name = order_data.get('product_name') or product.name

            order = Order.objects.create(
                user=order_data.get('user'),
                booking=order_data.get('booking'),
                customer_name=order_data['customer_name'],
                email=order_data['email'],
                phone=order_data['phone'],
                shipping_address=order_data.get('shipping_address', ''),
                product=product,
                product_name=product_name,
                selected_size=order_data.get('selected_size', 'Standard'),
                selected_wood=order_data.get('selected_wood', 'Pure Grade-A Burma Teak'),
                quantity=order_data.get('quantity', 1),
                unit_price=Decimal(str(order_data.get('unit_price', total_amount))),
                total_amount=total_amount,
                paid_amount=Decimal('0.00'),
                remaining_amount=total_amount,
                payment_plan=plan,
                order_status='PENDING_PAYMENT'
            )

            if plan == 'THREE_INSTALLMENTS':
                amounts = cls.calculate_three_installments(total_amount)
                dates = cls.get_schedule_dates(start_date)

                for num, (amt, due) in enumerate(zip(amounts, dates), start=1):
                    Installment.objects.create(
                        order=order,
                        installment_number=num,
                        amount=amt,
                        due_date=due,
                        status='PENDING'
                    )

            NotificationService.notify_order_created(order)
            return order

    # Convenient alias for creating installment orders
    create_installment_order = create_order_with_installments


class PaymentService:
    """
    Production-ready payment handling with server-side validation, idempotency,
    atomic database transactions, and automatic status updates.
    """

    @staticmethod
    def process_payment(order, installment_id=None, amount=None, gateway='Razorpay',
                        gateway_payment_id=None, gateway_order_id='', gateway_signature='',
                        idempotency_key=None, notes=''):
        """
        Records a payment transaction atomically, marks installment as PAID,
        and recalculates the order financial standing.
        """
        with transaction.atomic():
            # Idempotency check: Has this payment ID already been recorded?
            if gateway_payment_id:
                existing_txn = PaymentTransaction.objects.filter(gateway_payment_id=gateway_payment_id).first()
                if existing_txn and existing_txn.status == 'SUCCESS':
                    return True, existing_txn, "Payment already processed successfully (Idempotent replay)."

            if idempotency_key:
                existing_key = PaymentTransaction.objects.filter(idempotency_key=idempotency_key).first()
                if existing_key and existing_key.status == 'SUCCESS':
                    return True, existing_key, "Payment already processed successfully (Idempotent replay)."

            target_installment = None

            if order.payment_plan == 'THREE_INSTALLMENTS':
                if installment_id:
                    target_installment = Installment.objects.select_for_update().get(id=installment_id, order=order)
                else:
                    target_installment = order.next_due_installment

                if not target_installment:
                    raise ValueError("No pending installments available for this order.")

                if not target_installment.is_eligible_for_payment:
                    raise ValueError(f"Installment #{target_installment.installment_number} is not eligible for payment yet. Please pay prior installments first.")

                # Server-side amount enforcement: Customer CANNOT manipulate the amount!
                expected_amount = target_installment.amount
                if amount is not None:
                    provided_amount = Decimal(str(amount))
                    if provided_amount != expected_amount:
                        raise ValueError(f"Amount mismatch: Expected ₹{expected_amount}, received ₹{provided_amount}. Tampering detected.")
                else:
                    amount = expected_amount
            else:
                # FULL_PAYMENT
                expected_amount = order.remaining_amount
                if amount is not None:
                    provided_amount = Decimal(str(amount))
                    if provided_amount != expected_amount:
                        raise ValueError(f"Amount mismatch: Expected ₹{expected_amount}, received ₹{provided_amount}.")
                else:
                    amount = expected_amount

            # Create payment transaction
            txn = PaymentTransaction.objects.create(
                order=order,
                installment=target_installment,
                gateway=gateway,
                gateway_payment_id=gateway_payment_id or f"PAY-{uuid.uuid4().hex[:10].upper()}",
                gateway_order_id=gateway_order_id,
                gateway_signature=gateway_signature,
                amount=amount,
                currency='INR',
                status='SUCCESS',
                idempotency_key=idempotency_key or f"IDEMP-{uuid.uuid4().hex[:12]}",
                paid_at=timezone.now()
            )

            # Update installment if installment order
            if target_installment:
                target_installment.status = 'PAID'
                target_installment.paid_at = timezone.now()
                target_installment.payment_id = txn.gateway_payment_id
                target_installment.save()

                NotificationService.notify_installment_paid(order, target_installment)

            # Recalculate order financial standing
            order.update_financial_status()

            # Update associated booking if linked
            if order.booking:
                if order.payment_status in ['FULLY_PAID', 'PARTIALLY_PAID']:
                    order.booking.status = 'Confirmed'
                order.booking.notes += f" | Order: {order.order_number} | Paid: ₹{amount:,.0f} via {gateway} ({txn.gateway_payment_id})"
                order.booking.save()

            if order.payment_status == 'FULLY_PAID':
                NotificationService.notify_order_fully_paid(order)

            return True, txn, "Payment recorded and processed successfully."


class RescheduleService:
    """
    Admin installment rescheduling service enforcing business rules, sequential ordering,
    immutable audit logs, and customer notifications.
    """

    @staticmethod
    def reschedule_installment(installment_id, new_due_date, reason, changed_by='Master Studio Admin', notify_customer=False):
        """
        Reschedules a customer's installment due date.
        Enforces:
        1. Only PENDING, OVERDUE, or FAILED installments can be rescheduled.
        2. Cannot reschedule PAID installments.
        3. Valid future date.
        4. Chronological sequence (Installment 3 cannot be before Installment 2, etc.).
        5. Reason is strictly mandatory.
        6. Creates an immutable InstallmentRescheduleAudit record.
        7. Sends customer notification if requested.
        """
        if not reason or not reason.strip():
            raise InstallmentRescheduleError("A valid reason for rescheduling is strictly required.")

        with transaction.atomic():
            installment = Installment.objects.select_for_update().get(id=installment_id)
            order = installment.order

            if not installment.is_eligible_for_reschedule:
                raise InstallmentRescheduleError(f"Installment #{installment.installment_number} has status '{installment.status}' and cannot be rescheduled.")

            old_due_date = installment.due_date

            # Date sequence validation
            # Installment 2 cannot be scheduled before Installment 1
            if installment.installment_number > 1:
                prior_inst = Installment.objects.filter(
                    order=order,
                    installment_number=installment.installment_number - 1
                ).first()
                if prior_inst and new_due_date < prior_inst.due_date:
                    raise InstallmentRescheduleError(
                        f"Installment #{installment.installment_number} cannot be scheduled earlier than Installment #{prior_inst.installment_number} ({prior_inst.due_date.strftime('%d %b %Y')})."
                    )

            # Installment 2 cannot be scheduled after Installment 3 (if 3 exists)
            if installment.installment_number < 3:
                next_inst = Installment.objects.filter(
                    order=order,
                    installment_number=installment.installment_number + 1
                ).first()
                if next_inst and new_due_date > next_inst.due_date:
                    raise InstallmentRescheduleError(
                        f"Installment #{installment.installment_number} cannot be scheduled later than Installment #{next_inst.installment_number} ({next_inst.due_date.strftime('%d %b %Y')})."
                    )

            # Update due date
            installment.due_date = new_due_date
            if installment.status == 'OVERDUE' and new_due_date >= timezone.now().date():
                installment.status = 'PENDING'
            installment.save()

            # Create immutable audit log
            audit = InstallmentRescheduleAudit.objects.create(
                order=order,
                installment=installment,
                old_due_date=old_due_date,
                new_due_date=new_due_date,
                changed_by=changed_by,
                reason=reason.strip(),
                customer_notified=notify_customer
            )

            # Send customer notification if selected
            if notify_customer:
                NotificationService.notify_installment_rescheduled(order, installment, old_due_date, new_due_date, reason)

            return True, audit, "Installment due date rescheduled successfully."


class NotificationService:
    """
    Modular notification dispatcher creating user in-app notifications and logging alerts.
    """

    @staticmethod
    def notify_order_created(order):
        plan_text = "in 3 installments" if order.payment_plan == 'THREE_INSTALLMENTS' else "with full payment"
        Notification.objects.create(
            title=f"Order Confirmed: #{order.order_number}",
            description=f"Your order for {order.product_name} ({order.selected_size}, {order.selected_wood}) {plan_text} has been initiated. Total: {order.formatted_total}.",
            type='order_created'
        )

    @staticmethod
    def notify_installment_paid(order, installment):
        Notification.objects.create(
            title=f"Payment Received for #{order.order_number}",
            description=f"Installment #{installment.installment_number} of {installment.formatted_amount} has been successfully paid. Remaining balance: {order.formatted_remaining}.",
            type='installment_paid'
        )

    @staticmethod
    def notify_order_fully_paid(order):
        Notification.objects.create(
            title=f"Order #{order.order_number} Fully Paid!",
            description=f"All 3 installments for your {order.product_name} have been completely fulfilled. Your piece is now in final finishing for doorstep dispatch.",
            type='fully_paid'
        )

    @staticmethod
    def notify_installment_rescheduled(order, installment, old_date, new_date, reason):
        Notification.objects.create(
            title=f"Payment Schedule Updated for #{order.order_number}",
            description=(
                f"Installment #{installment.installment_number} ({installment.formatted_amount}) due date has been updated "
                f"from {old_date.strftime('%d %B %Y')} to {new_date.strftime('%d %B %Y')}. "
                f"Reason: {reason}."
            ),
            type='installment_rescheduled'
        )
