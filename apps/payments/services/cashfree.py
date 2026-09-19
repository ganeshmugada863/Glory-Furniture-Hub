import uuid
import re
import logging
import requests
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger('glory_furniture.payments')


class CashfreeAPIError(Exception):
    def __init__(self, message, status_code=None, raw_response=None):
        super().__init__(message)
        self.status_code = status_code
        self.raw_response = raw_response or {}


class CashfreeService:
    """
    Official Cashfree Payment Gateway integration (API Version 2023-08-01).
    Handles server-side order creation, payment status retrieval, and refunds.
    """

    @classmethod
    def get_base_url(cls):
        env = getattr(settings, 'CASHFREE_ENVIRONMENT', 'SANDBOX').upper()
        if env == 'PRODUCTION':
            return 'https://api.cashfree.com'
        return 'https://sandbox.cashfree.com'

    @classmethod
    def get_headers(cls):
        client_id = getattr(settings, 'CASHFREE_CLIENT_ID', '')
        client_secret = getattr(settings, 'CASHFREE_CLIENT_SECRET', '')
        api_version = getattr(settings, 'CASHFREE_API_VERSION', '2023-08-01')

        return {
            'Content-Type': 'application/json',
            'x-client-id': client_id,
            'x-client-secret': client_secret,
            'x-api-version': api_version,
            'x-request-id': str(uuid.uuid4()),
        }

    @classmethod
    def is_configured(cls):
        client_id = getattr(settings, 'CASHFREE_CLIENT_ID', '').strip()
        client_secret = getattr(settings, 'CASHFREE_CLIENT_SECRET', '').strip()
        return bool(client_id and client_secret and client_id != 'YOUR_CLIENT_ID')

    @classmethod
    def sanitize_phone(cls, phone):
        """
        Sanitizes customer phone number to clean digits.
        Strictly prevents using or returning unauthorized dummy numbers.
        """
        if not phone:
            return ''
        digits = re.sub(r'\D', '', str(phone))
        if len(digits) == 12 and digits.startswith('91'):
            digits = digits[2:]
        if len(digits) > 10:
            digits = digits[-10:]
        if digits in ['9876543210', '09876543210']:
            return ''
        return digits

    @classmethod
    def create_order(cls, order, installment=None, return_url=None, notify_url=None):
        """
        Creates an order on Cashfree server-side and returns payment_session_id.
        Amount is strictly determined server-side from order or installment.
        """
        if installment:
            payable_amount = installment.amount
            cf_order_id = f"CF_INST_{installment.id}_{uuid.uuid4().hex[:6].upper()}"
            order_note = f"Glory Furniture Hub - Installment #{installment.installment_number} for Order {order.order_number}"
        else:
            payable_amount = order.remaining_amount or order.total_amount
            cf_order_id = f"CF_ORD_{order.id}_{uuid.uuid4().hex[:6].upper()}"
            order_note = f"Glory Furniture Hub - Full Payment for Order {order.order_number}"

        amount_float = float(Decimal(str(payable_amount)).quantize(Decimal('0.01')))

        # Customer details - strictly use customer's legitimate phone
        customer_id = f"CUST_{order.user_id or order.id or uuid.uuid4().hex[:6]}"
        customer_name = order.customer_name or 'Valued Patron'
        customer_email = order.email or 'patron@gloryfurniturehub.com'
        customer_phone = cls.sanitize_phone(order.phone)
        if not customer_phone and getattr(order, 'user', None) and getattr(order.user, 'profile', None):
            customer_phone = cls.sanitize_phone(order.user.profile.phone)

        if not customer_phone or len(customer_phone) < 10:
            raise ValueError("A valid 10-digit customer phone number is required to initiate a Cashfree payment session.")

        # URLs
        if not return_url:
            return_url = f"https://glory-furniture-hub.onrender.com/payments/return/?order_id={cf_order_id}"
        if not notify_url:
            notify_url = "https://glory-furniture-hub.onrender.com/payments/webhook/cashfree/"

        cust_details = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        }

        payload = {
            "order_id": cf_order_id,
            "order_amount": amount_float,
            "order_currency": "INR",
            "customer_details": cust_details,
            "order_meta": {
                "return_url": return_url,
                "notify_url": notify_url,
            },
            "order_note": order_note,
        }

        # If credentials are not yet set in environment, generate local development session
        if not cls.is_configured():
            logger.warning("Cashfree credentials not configured. Generating sandbox simulation session.")
            simulated_session_id = f"session_simulated_{uuid.uuid4().hex}"
            return {
                "order_id": cf_order_id,
                "payment_session_id": simulated_session_id,
                "order_status": "ACTIVE",
                "order_amount": amount_float,
                "is_simulated": True,
                "raw_response": {"message": "Simulated sandbox order without active Cashfree keys."}
            }

        url = f"{cls.get_base_url()}/pg/orders"
        try:
            resp = requests.post(url, json=payload, headers=cls.get_headers(), timeout=15)
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"Cashfree Order API network error: {e}")
            raise CashfreeAPIError("Unable to connect to Cashfree payment server. Please try again shortly.") from e

        if resp.status_code not in [200, 201]:
            err_msg = data.get('message') or data.get('error') or "Cashfree order creation failed."
            logger.error(f"Cashfree Order Error ({resp.status_code}): {data}")
            raise CashfreeAPIError(err_msg, status_code=resp.status_code, raw_response=data)

        return {
            "order_id": data.get("order_id", cf_order_id),
            "payment_session_id": data.get("payment_session_id"),
            "order_status": data.get("order_status"),
            "order_amount": data.get("order_amount"),
            "cf_order_id": data.get("cf_order_id"),
            "is_simulated": False,
            "raw_response": data
        }

    @classmethod
    def get_order_payments(cls, cf_order_id):
        """
        Retrieves all payments made for a Cashfree order from `/pg/orders/{order_id}/payments`.
        """
        if not cls.is_configured() or cf_order_id.startswith('CF_') and 'simulated' in cf_order_id:
            return [{
                "payment_status": "SUCCESS",
                "cf_payment_id": f"CF_PAY_SIM_{uuid.uuid4().hex[:8].upper()}",
                "payment_amount": 1000.0,
                "payment_currency": "INR",
                "payment_method": {"upi": {"channel": "intent"}},
                "is_simulated": True
            }]

        url = f"{cls.get_base_url()}/pg/orders/{cf_order_id}/payments"
        try:
            resp = requests.get(url, headers=cls.get_headers(), timeout=15)
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"Cashfree Payment Status API network error: {e}")
            raise CashfreeAPIError("Unable to verify payment status with Cashfree.") from e

        if resp.status_code != 200:
            err_msg = data.get('message') if isinstance(data, dict) else "Could not retrieve payments."
            raise CashfreeAPIError(err_msg, status_code=resp.status_code, raw_response=data)

        return data if isinstance(data, list) else []

    @classmethod
    def get_order_details(cls, cf_order_id):
        """
        Retrieves order details from `/pg/orders/{order_id}`.
        """
        if not cls.is_configured():
            return {
                "order_id": cf_order_id,
                "order_status": "PAID",
                "is_simulated": True
            }

        url = f"{cls.get_base_url()}/pg/orders/{cf_order_id}"
        try:
            resp = requests.get(url, headers=cls.get_headers(), timeout=15)
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"Cashfree Order Details API error: {e}")
            raise CashfreeAPIError("Unable to retrieve order details from Cashfree.") from e

        if resp.status_code != 200:
            err_msg = data.get('message', 'Failed to retrieve order details.')
            raise CashfreeAPIError(err_msg, status_code=resp.status_code, raw_response=data)

        return data

    @classmethod
    def create_refund(cls, cf_order_id, refund_amount, refund_id=None, refund_note="Customer Refund"):
        """
        Initiates a refund via Cashfree `/pg/orders/{order_id}/refunds`.
        """
        if not refund_id:
            refund_id = f"REF_{uuid.uuid4().hex[:10].upper()}"

        payload = {
            "refund_amount": float(Decimal(str(refund_amount)).quantize(Decimal('0.01'))),
            "refund_id": refund_id,
            "refund_note": refund_note
        }

        if not cls.is_configured():
            return {
                "refund_id": refund_id,
                "refund_status": "SUCCESS",
                "refund_amount": payload["refund_amount"],
                "is_simulated": True
            }

        url = f"{cls.get_base_url()}/pg/orders/{cf_order_id}/refunds"
        try:
            resp = requests.post(url, json=payload, headers=cls.get_headers(), timeout=15)
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"Cashfree Refund API error: {e}")
            raise CashfreeAPIError("Network error contacting Cashfree refund service.") from e

        if resp.status_code not in [200, 201]:
            err_msg = data.get('message', 'Refund request failed.')
            raise CashfreeAPIError(err_msg, status_code=resp.status_code, raw_response=data)

        return data
