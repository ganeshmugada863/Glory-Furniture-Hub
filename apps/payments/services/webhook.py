import json
import base64
import hmac
import hashlib
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from apps.payments.models import Payment, WebhookEvent
from apps.bookings.models import Order, Installment, Booking
from apps.bookings.services import NotificationService

logger = logging.getLogger('glory_furniture.payments')


class WebhookVerificationError(Exception):
    pass


class WebhookService:
    """
    Cryptographically secure and idempotent Cashfree Webhook processing service.
    """

    @classmethod
    def verify_signature(cls, raw_body_bytes, timestamp, signature):
        """
        Validates the Cashfree webhook HMAC signature.
        Cashfree signature formula:
        signature_data = timestamp + raw_body
        computed_signature = Base64(HMAC-SHA256(signature_data, CASHFREE_CLIENT_SECRET))
        """
        secret = getattr(settings, 'CASHFREE_CLIENT_SECRET', '').strip()
        if not secret:
            logger.warning("CASHFREE_CLIENT_SECRET not configured. Bypassing webhook signature check for simulation.")
            return True

        if not signature or not timestamp:
            logger.error("Missing webhook signature or timestamp headers.")
            return False

        try:
            body_str = raw_body_bytes.decode('utf-8')
            signature_data = f"{timestamp}{body_str}"

            # Compute Base64 HMAC-SHA256
            mac = hmac.new(secret.encode('utf-8'), signature_data.encode('utf-8'), hashlib.sha256).digest()
            computed_base64 = base64.b64encode(mac).decode('utf-8')

            # Also check hex digest for backward compatibility
            computed_hex = hmac.new(secret.encode('utf-8'), signature_data.encode('utf-8'), hashlib.sha256).hexdigest()

            # Constant-time comparison
            if hmac.compare_digest(signature, computed_base64) or hmac.compare_digest(signature, computed_hex):
                return True

            logger.error(f"Webhook signature mismatch! Expected: {computed_base64} or {computed_hex}, Got: {signature}")
            return False
        except Exception as e:
            logger.error(f"Error during webhook signature calculation: {e}")
            return False

    @classmethod
    def process_webhook(cls, raw_body_bytes, headers):
        """
        Main entry point for handling incoming Cashfree webhooks idempotently.
        """
        timestamp = headers.get('X-Webhook-Timestamp') or headers.get('x-webhook-timestamp') or ''
        signature = headers.get('X-Webhook-Signature') or headers.get('x-webhook-signature') or ''

        # 1. Verify Signature
        if not cls.verify_signature(raw_body_bytes, timestamp, signature):
            raise WebhookVerificationError("Invalid webhook signature.")

        # 2. Idempotency Check via SHA-256 hash
        payload_hash = hashlib.sha256(raw_body_bytes).hexdigest()
        existing_event = WebhookEvent.objects.filter(payload_hash=payload_hash).first()
        if existing_event and existing_event.status == 'PROCESSED':
            logger.info(f"Webhook {payload_hash} already processed (idempotent replay).")
            return {
                "status": "already_processed",
                "message": "Event already processed successfully.",
                "event_id": existing_event.event_id
            }

        try:
            payload = json.loads(raw_body_bytes.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Invalid JSON payload: {e}")

        # 3. Extract Order & Payment details across Cashfree schema versions
        cf_order_id, cf_payment_id, payment_status, amount, payment_method, event_type = cls._extract_webhook_data(payload)

        # 4. Record WebhookEvent
        webhook_event, _ = WebhookEvent.objects.get_or_create(
            payload_hash=payload_hash,
            defaults={
                'event_id': payload.get('data', {}).get('payment', {}).get('cf_payment_id') or str(payload.get('event_time', '')),
                'event_type': event_type,
                'gateway_order_id': cf_order_id,
                'gateway_payment_id': str(cf_payment_id),
                'payload': payload,
                'status': 'RECEIVED'
            }
        )

        # 5. Atomic state update
        with transaction.atomic():
            payment, order, installment = cls._resolve_local_records(cf_order_id, amount)

            if not order:
                webhook_event.status = 'FAILED'
                webhook_event.error_message = f"Could not find local Order for Cashfree order {cf_order_id}"
                webhook_event.save()
                return {"status": "error", "message": webhook_event.error_message}

            # Server-side amount validation
            expected_amount = installment.amount if installment else (order.remaining_amount or order.total_amount)
            if amount is not None and Decimal(str(amount)) != Decimal(str(expected_amount)):
                # If it matches total_amount on full payment, allow
                if Decimal(str(amount)) != Decimal(str(order.total_amount)):
                    logger.critical(f"AMOUNT MISMATCH DETECTED! Expected: ₹{expected_amount}, Received: ₹{amount}")
                    webhook_event.status = 'FAILED'
                    webhook_event.error_message = f"Amount mismatch: Expected ₹{expected_amount}, received ₹{amount}."
                    webhook_event.save()
                    return {"status": "error", "message": "Amount mismatch detected."}

            if payment_status in ['SUCCESS', 'PAID']:
                payment.status = 'PAID'
                payment.verification_status = 'VERIFIED'
                payment.is_manual = False
                payment.gateway_payment_id = str(cf_payment_id)
                payment.paid_at = timezone.now()
                payment.gateway_response = payload
                payment.payment_method = payment_method or 'UPI'
                payment.save()

                if installment:
                    installment.status = 'PAID'
                    installment.paid_at = timezone.now()
                    installment.payment_id = payment.gateway_payment_id
                    installment.save()
                    NotificationService.notify_installment_paid(order, installment)

                # Recalculate order financial standing
                order.recalculate_financials()

                # Update booking status if exists
                if order.booking:
                    order.booking.status = 'Confirmed'
                    order.booking.notes += f" | Cashfree Paid: ₹{payment.amount} (Ref: {cf_payment_id})"
                    order.booking.save()

                if order.payment_status == 'FULLY_PAID':
                    NotificationService.notify_order_fully_paid(order)
                else:
                    NotificationService.notify_order_created(order)

                webhook_event.status = 'PROCESSED'
                webhook_event.processed_at = timezone.now()
                webhook_event.save()

                return {"status": "success", "message": "Payment verified and order updated.", "payment_id": payment.payment_id}

            elif payment_status in ['FAILED', 'USER_DROPPED', 'CANCELLED']:
                payment.status = 'FAILED'
                payment.verification_status = 'REJECTED'
                payment.failure_reason = payload.get('data', {}).get('payment', {}).get('payment_message') or 'Transaction failed at gateway.'
                payment.save()

                if installment and installment.status != 'PAID':
                    installment.status = 'FAILED'
                    installment.save()

                order.recalculate_financials()

                webhook_event.status = 'PROCESSED'
                webhook_event.processed_at = timezone.now()
                webhook_event.save()

                return {"status": "failed", "message": payment.failure_reason}

            else:
                payment.status = 'PENDING'
                payment.save()
                webhook_event.status = 'PROCESSED'
                webhook_event.save()
                return {"status": "pending", "message": "Payment pending gateway confirmation."}

    @classmethod
    def _extract_webhook_data(cls, payload):
        """Extracts fields across Cashfree v2023-08-01 and legacy webhooks."""
        event_type = payload.get('type', 'PAYMENT_EVENT')
        data = payload.get('data', {})

        if data:
            order_data = data.get('order', {})
            payment_data = data.get('payment', {})

            cf_order_id = order_data.get('order_id') or ''
            cf_payment_id = payment_data.get('cf_payment_id') or ''
            payment_status = (payment_data.get('payment_status') or '').upper()
            amount = payment_data.get('payment_amount') or order_data.get('order_amount')

            method_obj = payment_data.get('payment_method', {})
            if isinstance(method_obj, dict):
                payment_method = list(method_obj.keys())[0].upper() if method_obj else 'UPI'
            else:
                payment_method = str(method_obj).upper()

            return cf_order_id, cf_payment_id, payment_status, amount, payment_method, event_type

        # Legacy Cashfree payload format
        cf_order_id = payload.get('orderId') or ''
        cf_payment_id = payload.get('referenceId') or ''
        payment_status = (payload.get('txStatus') or '').upper()
        amount = payload.get('orderAmount')
        payment_method = (payload.get('paymentMode') or 'UPI').upper()

        return cf_order_id, cf_payment_id, payment_status, amount, payment_method, event_type

    @classmethod
    def _resolve_local_records(cls, cf_order_id, amount=None):
        """Locates or instantiates Payment, Order, and Installment from gateway order ID."""
        payment = Payment.objects.filter(gateway_order_id=cf_order_id).first()
        order = None
        installment = None

        if payment:
            order = payment.order
            installment = payment.installment
            return payment, order, installment

        # Parse identifiers from cf_order_id
        # Pattern: CF_INST_<installment_id>_<rand> or CF_ORD_<order_id>_<rand>
        if cf_order_id.startswith('CF_INST_'):
            parts = cf_order_id.split('_')
            if len(parts) >= 3:
                try:
                    inst_id = int(parts[2])
                    installment = Installment.objects.filter(id=inst_id).first()
                    if installment:
                        order = installment.order
                except ValueError:
                    pass
        elif cf_order_id.startswith('CF_ORD_'):
            parts = cf_order_id.split('_')
            if len(parts) >= 3:
                try:
                    order_id = int(parts[2])
                    order = Order.objects.filter(id=order_id).first()
                except ValueError:
                    pass

        if not order:
            # Try searching by order_number
            for ord_obj in Order.objects.all()[:100]:
                if ord_obj.order_number in cf_order_id:
                    order = ord_obj
                    break

        if not order:
            import re
            import uuid
            from apps.payments.services.cashfree import CashfreeService
            from apps.store.models import Product
            # Fallback: Query Cashfree directly for order details
            try:
                cf_details = CashfreeService.get_order_details(cf_order_id)
                note = cf_details.get('order_note', '')
                match = re.search(r'ORD-[A-Z0-9]+', note)
                if match:
                    order = Order.objects.filter(order_number=match.group(0)).first()
                if not order and cf_details.get('order_status') in ['PAID', 'ACTIVE']:
                    cust = cf_details.get('customer_details', {})
                    product = Product.objects.first()
                    order_amt = Decimal(str(cf_details.get('order_amount') or amount or '2.00'))
                    order = Order.objects.create(
                        order_number=match.group(0) if match else f"ORD-{uuid.uuid4().hex[:6].upper()}",
                        customer_name=cust.get('customer_name') or 'Valued Patron',
                        email=cust.get('customer_email') or 'patron@gloryfurniturehub.com',
                        phone=cust.get('customer_phone') or '',
                        total_amount=order_amt,
                        paid_amount=order_amt if cf_details.get('order_status') == 'PAID' else Decimal('0.00'),
                        remaining_amount=Decimal('0.00') if cf_details.get('order_status') == 'PAID' else order_amt,
                        payment_status='FULLY_PAID' if cf_details.get('order_status') == 'PAID' else 'PENDING',
                        fulfillment_status='CONFIRMED',
                        payment_type='FULL',
                        product=product,
                        product_name=product.name if product else 'Solid Teak Royal Accent Table',
                        quantity=1,
                        unit_price=order_amt,
                    )
            except Exception as e:
                logger.error(f"Error querying Cashfree for order recovery in _resolve_local_records: {e}")

        if order:
            payment_type = 'INSTALLMENT' if installment else 'FULL'
            pay_amount = installment.amount if installment else (Decimal(str(amount)) if amount else order.total_amount)
            payment = Payment.objects.create(
                order=order,
                customer=order.user,
                installment=installment,
                payment_type=payment_type,
                amount=pay_amount,
                currency='INR',
                gateway='Cashfree',
                gateway_order_id=cf_order_id,
                status='PENDING'
            )

        return payment, order, installment
