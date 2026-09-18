import logging
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from apps.payments.models import Payment
from apps.bookings.models import Order, Installment, OrderAdminAuditLog

logger = logging.getLogger("glory_furniture.payments")


class ManualPaymentError(Exception):
    pass


class ManualPaymentService:
    """
    Official admin manual payment workflow service.
    Handles recording, verification, and rejection of manual offline/UPI/cash/bank payments.
    Guarantees that unverified payments do NOT count toward order financial totals.
    """

    ALLOWED_METHODS = ["CASH", "UPI", "BANK_TRANSFER", "OFFLINE", "OTHER"]

    @classmethod
    def record_manual_payment(
        cls,
        order,
        amount,
        payment_method,
        reference_number="",
        payment_date=None,
        installment=None,
        installment_id=None,
        notes="",
        receipt_image="",
        admin_user=None,
    ):
        if not order:
            raise ManualPaymentError("Order is required.")

        try:
            amt_dec = Decimal(str(amount))
        except Exception as e:
            raise ManualPaymentError(f"Invalid payment amount: {amount}") from e

        if amt_dec <= Decimal("0.00"):
            raise ManualPaymentError("Manual payment amount must be greater than zero.")

        if amt_dec > order.remaining_amount:
            raise ManualPaymentError(
                f"Payment amount (₹{amt_dec}) exceeds remaining order balance (₹{order.remaining_amount})."
            )

        pm_upper = (payment_method or "OTHER").strip().upper()
        if pm_upper not in cls.ALLOWED_METHODS:
            raise ManualPaymentError(f"Unsupported manual payment method '{payment_method}'. Allowed: {cls.ALLOWED_METHODS}")

        ref_clean = (reference_number or "").strip()
        if ref_clean:
            # Check for duplicate verified reference number across payments
            if Payment.objects.filter(reference_number=ref_clean, verification_status="VERIFIED").exists():
                raise ManualPaymentError(f"Reference number '{ref_clean}' has already been verified for another transaction.")

        # Validate installment if provided
        target_installment = None
        inst_target = installment or installment_id
        if inst_target:
            if isinstance(inst_target, (int, str)) and str(inst_target).isdigit():
                target_installment = order.installments.filter(id=int(inst_target)).first()
            elif hasattr(inst_target, "id"):
                target_installment = inst_target

            if not target_installment or target_installment.order_id != order.id:
                raise ManualPaymentError("Specified installment does not belong to this order.")

            if target_installment.status == "PAID":
                raise ManualPaymentError(f"Installment #{target_installment.installment_number} is already paid.")

            if amt_dec > target_installment.amount:
                raise ManualPaymentError(
                    f"Amount ₹{amt_dec} exceeds installment amount ₹{target_installment.amount}."
                )

        # Determine effective payment date (Payment Date vs Created Date)
        effective_payment_date = payment_date or timezone.now()
        if hasattr(effective_payment_date, 'date') and not hasattr(effective_payment_date, 'hour'):
            effective_payment_date = timezone.datetime.combine(
                effective_payment_date, timezone.now().time()
            ).replace(tzinfo=timezone.get_current_timezone())

        with transaction.atomic():
            payment = Payment.objects.create(
                order=order,
                customer=order.user,
                installment=target_installment,
                payment_type="INSTALLMENT" if target_installment else "FULL",
                amount=amt_dec,
                currency="INR",
                gateway="Manual",
                payment_method=pm_upper,
                reference_number=ref_clean,
                status="PENDING",
                is_manual=True,
                verification_status="PENDING_VERIFICATION",
                admin_notes=notes or "",
                receipt_image=receipt_image or "",
                paid_at=effective_payment_date,
            )

            OrderAdminAuditLog.objects.create(
                order=order,
                action="MANUAL_PAYMENT_ADDED",
                performed_by=admin_user,
                old_value="",
                new_value=f"{pm_upper} ₹{amt_dec} (Ref: {ref_clean or 'N/A'})",
                amount=amt_dec,
                notes=f"Recorded manual payment {payment.payment_id}. Status: PENDING_VERIFICATION. Paid Date: {effective_payment_date.strftime('%Y-%m-%d %H:%M')}. Notes: {notes}",
            )

            # Note: Do not count unverified payment in order financials
            logger.info(f"Recorded manual payment {payment.payment_id} for order {order.order_number}. Awaiting verification.")
            return payment

    @classmethod
    def verify_manual_payment(cls, payment_id, admin_user, verification_notes=""):
        payment = Payment.objects.filter(payment_id=payment_id).first() or Payment.objects.filter(id=payment_id).first()
        if not payment:
            raise ManualPaymentError(f"Payment '{payment_id}' not found.")

        if not payment.is_manual:
            raise ManualPaymentError("Only manual payments can be manually verified.")

        if payment.verification_status == "VERIFIED":
            logger.warning(f"Payment {payment.payment_id} is already verified.")
            return payment

        order = payment.order
        with transaction.atomic():
            payment.verification_status = "VERIFIED"
            payment.status = "PAID"
            payment.verified_by = admin_user
            payment.verified_at = timezone.now()
            # Preserve the actual payment date (paid_at) previously entered by admin
            payment.paid_at = payment.paid_at or timezone.now()
            if verification_notes:
                payment.admin_notes = f"{payment.admin_notes} | Verified notes: {verification_notes}".strip(" |")
            payment.save()

            # Recalculate order financials and installment milestone completion mathematically
            # Prevents prematurely marking installments or orders as PAID on partial amounts
            order.recalculate_financials()

            OrderAdminAuditLog.objects.create(
                order=order,
                action="MANUAL_PAYMENT_VERIFIED",
                performed_by=admin_user,
                old_value="PENDING_VERIFICATION",
                new_value="VERIFIED",
                amount=payment.amount,
                notes=f"Verified manual payment {payment.payment_id}. New order paid balance: ₹{order.paid_amount}",
            )

            logger.info(f"Verified manual payment {payment.payment_id} for order {order.order_number}.")
            return payment

    @classmethod
    def reject_manual_payment(cls, payment_id, admin_user, reason="", rejection_reason=""):
        reason = (reason or rejection_reason or "").strip()
        payment = Payment.objects.filter(payment_id=payment_id).first() or Payment.objects.filter(id=payment_id).first()
        if not payment:
            raise ManualPaymentError(f"Payment '{payment_id}' not found.")

        if not payment.is_manual:
            raise ManualPaymentError("Only manual payments can be rejected.")

        if payment.verification_status == "REJECTED":
            return payment

        order = payment.order
        with transaction.atomic():
            payment.verification_status = "REJECTED"
            payment.status = "FAILED"
            payment.failure_reason = reason or "Rejected by administrator."
            payment.admin_notes = f"{payment.admin_notes} | Rejected by {admin_user}: {reason}".strip(" |")
            payment.save()

            # Recalculate order financials to ensure this payment does not count
            order.recalculate_financials()

            OrderAdminAuditLog.objects.create(
                order=order,
                action="MANUAL_PAYMENT_REJECTED",
                performed_by=admin_user,
                old_value=payment.verification_status,
                new_value="REJECTED",
                amount=payment.amount,
                notes=f"Rejected manual payment {payment.payment_id}. Reason: {reason}",
            )

            logger.info(f"Rejected manual payment {payment.payment_id} for order {order.order_number}.")
            return payment
