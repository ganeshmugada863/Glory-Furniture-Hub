import logging
from decimal import Decimal
from apps.payments.models import Payment
from apps.bookings.models import PaymentTransaction

logger = logging.getLogger("glory_furniture.payments")


class PaymentLedgerService:
    """
    Unified payment ledger service.
    Prioritizes modern Payment records and falls back to legacy PaymentTransaction records
    without double counting.
    """

    @classmethod
    def get_order_transactions(cls, order):
        """
        Returns a sorted, deduplicated list of all payment transactions for an order.
        Each item is a normalized dictionary.
        Enforces:
        - Multi-identifier deduplication across modern Payment and legacy PaymentTransaction records.
        - Preserves and exposes both paid_at (financial settlement date) and created_at (record audit date).
        - Prevents double-counting of migrated installment records.
        """
        entries = []
        known_refs = set()
        modern_paid_by_installment = {}

        # 1. Modern Payment records
        modern_payments = order.payments.all().order_by("-created_at")
        for p in modern_payments:
            ref = p.gateway_payment_id or p.reference_number or p.payment_id
            for ident in [p.payment_id, p.gateway_payment_id, p.reference_number, p.gateway_order_id]:
                if ident:
                    known_refs.add(str(ident).strip().upper())

            if p.installment_id and p.status == "PAID" and p.verification_status == "VERIFIED":
                modern_paid_by_installment[p.installment_id] = (
                    modern_paid_by_installment.get(p.installment_id, Decimal("0.00")) + p.amount
                )

            entries.append({
                "id": p.id,
                "payment_id": p.payment_id,
                "amount": p.amount,
                "formatted_amount": f"₹{int(p.amount):,}",
                "status": p.status,
                "payment_type": p.payment_type,
                "payment_method": p.payment_method or ("CASHFREE" if not p.is_manual else "MANUAL"),
                "gateway": p.gateway,
                "is_manual": p.is_manual,
                "verification_status": p.verification_status,
                "reference": ref,
                "paid_at": p.paid_at,
                "created_at": p.created_at,
                "verified_at": p.verified_at,
                "verified_by": p.verified_by,
                "installment": p.installment,
                "installment_number": p.installment.installment_number if p.installment else None,
                "source": "Manual" if p.is_manual else "Cashfree",
                "notes": p.admin_notes or p.failure_reason,
                "is_verified": (p.verification_status == "VERIFIED" and p.status == "PAID"),
            })

        # 2. Legacy PaymentTransaction records (fallback, deduplicated)
        legacy_txs = order.transactions.all().order_by("-created_at")
        for t in legacy_txs:
            t_pid = (t.gateway_payment_id or "").strip().upper()
            t_goid = (t.gateway_order_id or "").strip().upper()
            t_idemp = (t.idempotency_key or "").strip().upper()
            legacy_id = f"LEGACY-{t.id}".upper()
            txn_id = f"TXN-{t.id}".upper()

            # Deduplication 1: Any matching identifier in known references
            if (t_pid and t_pid in known_refs) or (t_goid and t_goid in known_refs):
                continue
            if (legacy_id in known_refs) or (txn_id in known_refs):
                continue
            if t_idemp and any(t_idemp in k or k in t_idemp for k in known_refs):
                continue

            # Deduplication 2: Same installment already covered by modern verified payment
            if t.installment_id and t.installment_id in modern_paid_by_installment:
                if modern_paid_by_installment[t.installment_id] >= t.amount:
                    continue

            entries.append({
                "id": f"legacy_{t.id}",
                "payment_id": t.gateway_payment_id or f"TXN-{t.id}",
                "amount": t.amount,
                "formatted_amount": f"₹{int(t.amount):,}",
                "status": "PAID" if t.status == "SUCCESS" else t.status,
                "payment_type": "INSTALLMENT" if t.installment else "FULL",
                "payment_method": t.gateway or "UPI",
                "gateway": t.gateway or "Legacy Gateway",
                "is_manual": False,
                "verification_status": "VERIFIED" if t.status == "SUCCESS" else "PENDING_VERIFICATION",
                "reference": t.gateway_payment_id,
                "paid_at": t.paid_at,
                "created_at": t.created_at,
                "verified_at": t.paid_at,
                "verified_by": None,
                "installment": t.installment,
                "installment_number": t.installment.installment_number if t.installment else None,
                "source": "Legacy",
                "notes": t.failure_reason,
                "is_verified": (t.status == "SUCCESS"),
            })

        # Sort all entries: prioritize payment date (paid_at), then creation date descending
        entries.sort(key=lambda x: x["paid_at"] or x["created_at"], reverse=True)
        return entries
