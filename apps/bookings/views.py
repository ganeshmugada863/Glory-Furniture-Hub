import uuid
import re
import json
import hmac
import hashlib
from decimal import Decimal
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Booking, Order, Installment, PaymentTransaction, InstallmentRescheduleAudit, OrderStatusHistory, OrderAdminAuditLog
from .services import InstallmentService, PaymentService, RescheduleService, InstallmentRescheduleError
from apps.payments.models import Payment
from apps.payments.services import ManualPaymentService, PaymentLedgerService
from apps.store.models import Product


def booking_summary_view(request):
    """
    Renders the dedicated Order & Booking Summary page.
    Displays:
    1. Address Summary (delivery details, recipient, scheduling)
    2. Calculation of Item (product details, unit price, quantity, discount, GST, total)
    3. Payment Plan selection (Full Payment vs Three Installments) with transparent calculation.
    """
    # Check product or load from cart
    product_id = request.GET.get('product') or request.POST.get('product_id')
    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None
    cart = (profile.cart_items if profile else None) or request.session.get('glory_cart', [])

    selected_size = request.GET.get('bedSize') or request.GET.get('size') or request.POST.get('selected_size')
    quantity = None
    if not product_id and cart:
        primary_item = cart[0]
        product_id = primary_item.get('id')
        if not selected_size:
            selected_size = primary_item.get('size', 'Standard')
        quantity = int(primary_item.get('quantity', 1))

    try:
        product = Product.objects.filter(pk=int(product_id)).first() if product_id else None
    except (ValueError, TypeError):
        product = None

    if not product:
        product = Product.objects.first()

    if not selected_size:
        selected_size = 'Standard'

    selected_wood = request.GET.get('woodType') or request.GET.get('wood') or request.POST.get('selected_wood')
    if not selected_wood:
        selected_wood = product.finishes[0] if product and product.finishes else 'Natural Burma Teak'

    # Quantity & Pricing
    if quantity is None:
        try:
            quantity = int(request.GET.get('qty') or request.POST.get('quantity') or 1)
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

    try:
        raw_price = request.GET.get('price') or request.POST.get('unit_price')
        if raw_price:
            unit_price = float(raw_price)
        else:
            unit_price = float(product.price) if product else 24000.0
    except (ValueError, TypeError):
        unit_price = float(product.price) if product else 24000.0

    # Pricing calculations
    mrp = round(unit_price * 1.30, -2)
    discount_per_item = mrp - unit_price
    item_subtotal = unit_price * quantity
    total_mrp = mrp * quantity
    total_savings = discount_per_item * quantity
    delivery_charge = 0.0  # Free White-Glove in Hyderabad
    gst_included = round(item_subtotal * 0.18, 2)
    grand_total = item_subtotal + delivery_charge

    # Fetch saved address strictly from authenticated user profile first, then session
    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None

    addresses = (profile.saved_addresses if profile else None) or request.session.get('glory_addresses')
    if not addresses:
        default_address = {
            'id': 1,
            'tag': 'Home (Default)',
            'is_default': True,
            'name': profile.full_name if (profile and profile.full_name) else (user.get_full_name() if user else 'Valued Patron'),
            'phone': profile.phone if (profile and profile.phone) else '',
            'email': user.email if user else '',
            'flat': profile.address if (profile and profile.address) else 'Plot 42, Jubilee Hills',
            'street': 'Road No. 10',
            'landmark': '',
            'city': 'Hyderabad',
            'state': 'Telangana',
            'pincode': '500033',
        }
        addresses = [default_address]
        if profile:
            profile.saved_addresses = addresses
            profile.save(update_fields=['saved_addresses'])
        request.session['glory_addresses'] = addresses
    else:
        default_address = next((a for a in addresses if a.get('is_default')), addresses[0])

    if request.method == 'POST':
        # Strictly guarantee email & user association to prevent cross-account pollution
        if user:
            email = user.email
            customer_name = (profile.full_name if profile and profile.full_name else user.get_full_name()) or request.POST.get('customer_name', '').strip() or user.username
            phone = (profile.phone if profile and profile.phone else None) or request.POST.get('phone', '').strip() or ''
        else:
            email = request.POST.get('email', '').strip().lower() or default_address.get('email') or ''
            customer_name = request.POST.get('customer_name', '').strip() or default_address.get('name') or 'Valued Patron'
            phone = request.POST.get('phone', '').strip() or default_address.get('phone') or ''

        flat = request.POST.get('flat') or default_address.get('flat', '')
        street = request.POST.get('street') or default_address.get('street', '')
        landmark = request.POST.get('landmark') or default_address.get('landmark', '')
        city = request.POST.get('city') or default_address.get('city', 'Hyderabad')
        state = request.POST.get('state') or default_address.get('state', 'Telangana')
        pincode = request.POST.get('pincode') or default_address.get('pincode', '500034')

        full_address = f"{flat}, {street}, {landmark}, {city}, {state} - {pincode}".strip(', -')
        delivery_preference = request.POST.get('delivery_preference', 'Immediate Dispatch (5-7 Days)')
        payment_plan = 'FULL_PAYMENT'

        preferred_date = request.POST.get('preferred_date') or str(timezone.now().date() + timedelta(days=5))
        customer_notes = request.POST.get('notes', '').strip()

        prod_name = product.name if product else 'Handcrafted Teak Piece'
        order_notes = (
            f"Product: {prod_name} (ID #{product.id if product else product_id}) | "
            f"Size: {selected_size} | Finish: {selected_wood} | Qty: {quantity} | "
            f"Total: ₹{grand_total:,.0f} | Plan: Full Payment | Slot: {delivery_preference}"
        )
        if customer_notes:
            order_notes += f" | Note: {customer_notes}"

        # Create Order directly without fake Booking
        order = Order.objects.create(
            user=user,
            booking=None,
            customer_name=customer_name,
            email=email,
            phone=phone,
            shipping_address=full_address,
            product=product,
            product_name=prod_name,
            selected_size=selected_size,
            selected_wood=selected_wood,
            quantity=quantity,
            unit_price=Decimal(str(unit_price)),
            total_amount=Decimal(str(grand_total)),
            paid_amount=Decimal('0.00'),
            remaining_amount=Decimal(str(grand_total)),
            payment_plan='FULL_PAYMENT',
            payment_status='PENDING',
            fulfillment_status='CONFIRMED',
            order_status='PENDING_PAYMENT'
        )

        OrderStatusHistory.objects.create(
            order=order,
            fulfillment_status='CONFIRMED',
            previous_status='ORDER_PLACED',
            admin_notes='Order placed by patron at checkout.'
        )

        # Clear cart if order placed from cart
        if cart:
            if profile:
                profile.cart_items = []
                profile.save(update_fields=['cart_items'])
            request.session['glory_cart'] = []
            request.session.modified = True

        prod_img = product.primary_image if product and hasattr(product, 'primary_image') else ''
        request.session[f'order_payment_{order.order_number}'] = {
            'order_id': order.id,
            'order_number': order.order_number,
            'product_name': prod_name,
            'product_id': product.id if product else product_id,
            'product_image': prod_img,
            'selected_size': selected_size,
            'selected_wood': selected_wood,
            'quantity': quantity,
            'unit_price': float(unit_price),
            'grand_total': float(grand_total),
            'payment_plan': 'FULL_PAYMENT',
        }

        # Track order in customer session so it always appears in My Orders
        order_ids = request.session.get('glory_customer_order_ids', [])
        if order.id not in order_ids:
            order_ids.append(order.id)
        request.session['glory_customer_order_ids'] = order_ids
        request.session['glory_user_email'] = email
        request.session['glory_user_name'] = customer_name
        request.session['glory_user_phone'] = phone
        request.session['glory_role'] = 'customer'

        return redirect('payment_checkout', order_number=order.order_number)

    default_delivery_date = str(timezone.now().date() + timedelta(days=5))

    context = {
        'product': product,
        'selected_size': selected_size,
        'selected_wood': selected_wood,
        'quantity': quantity,
        'unit_price': unit_price,
        'mrp': mrp,
        'total_mrp': total_mrp,
        'total_savings': total_savings,
        'item_subtotal': item_subtotal,
        'delivery_charge': delivery_charge,
        'gst_included': gst_included,
        'grand_total': grand_total,
        'formatted_grand_total': f"₹{int(grand_total):,}",
        'formatted_unit_price': f"₹{int(unit_price):,}",
        'formatted_mrp': f"₹{int(mrp):,}",
        'formatted_subtotal': f"₹{int(item_subtotal):,}",
        'formatted_savings': f"₹{int(total_savings):,}",
        'formatted_gst': f"₹{int(gst_included):,}",
        'default_delivery_date': default_delivery_date,
        'saved_address': default_address,
        'user_name': (profile.full_name if profile and profile.full_name else (user.get_full_name() if user else None)) or default_address.get('name') or 'Valued Patron',
        'user_email': (user.email if user else None) or default_address.get('email') or '',
        'user_phone': (profile.phone if profile and profile.phone else None) or default_address.get('phone') or '',
    }
    return render(request, 'bookings/checkout_summary.html', context)


def booking_payment_view(request, booking_id):
    """
    Renders dedicated Payment Details page featuring the WordPress Direct UPI Gateway
    for 100% Full Payment.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id)
    order = Order.objects.filter(booking=booking).first()

    if not order:
        session_data = request.session.get(f'order_payment_{booking.booking_id}', {})
        prod_id = session_data.get('product_id') or 16
        product = Product.objects.filter(id=prod_id).first() or Product.objects.first()
        grand_total = Decimal(str(session_data.get('grand_total', 32000.0)))
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            booking=booking,
            customer_name=booking.customer_name,
            email=booking.email,
            phone=booking.phone,
            shipping_address=booking.address,
            product=product,
            product_name=product.name if product else 'Handcrafted Teak Furniture',
            selected_size=session_data.get('selected_size', 'Standard'),
            selected_wood=session_data.get('selected_wood', 'Pure Grade-A Burma Teak'),
            quantity=session_data.get('quantity', 1),
            unit_price=grand_total,
            total_amount=grand_total,
            paid_amount=Decimal('0.00'),
            remaining_amount=grand_total,
            payment_plan='FULL_PAYMENT',
            order_status='PENDING_PAYMENT',
        )

    payable_amount = order.total_amount
    upi_vpa = 'gloryfurniture@okaxis'
    payee_name = 'Glory Furniture Hub'
    upi_intent_url = f"upi://pay?pa={upi_vpa}&pn=Glory%20Furniture%20Hub&am={payable_amount:.2f}&cu=INR&tn=Order%20{order.order_number}"
    upi_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=260x260&data=upi%3A%2F%2Fpay%3Fpa%3D{upi_vpa}%26pn%3DGlory%2BFurniture%2BHub%26am%3D{payable_amount:.2f}%26cu%3DINR%26tn%3DOrder%2B{order.order_number}"

    if request.method == 'POST':
        payment_method = request.POST.get('payment_sub_method', 'WordPress UPI Gateway')
        utr_number = request.POST.get('utr_number', '').strip()

        if payment_method in ['WordPress UPI Gateway', 'UPI', 'Direct UPI']:
            if not utr_number:
                utr_number = f"4{uuid.uuid4().int % 100000000000:011d}"
            gateway_pay_id = f"UTR-{utr_number}"
            if PaymentTransaction.objects.filter(gateway_payment_id=gateway_pay_id).exists():
                gateway_pay_id = f"UTR-{utr_number}-{uuid.uuid4().hex[:4].upper()}"

            PaymentTransaction.objects.create(
                order=order,
                gateway='WordPress UPI Gateway',
                gateway_payment_id=gateway_pay_id,
                amount=payable_amount,
                currency='INR',
                status='SUCCESS',
                idempotency_key=f"IDEMP-UPI-{order.order_number}-{utr_number}",
                paid_at=timezone.now()
            )
            order.recalculate_financials()

            booking.status = 'Confirmed'
            booking.notes += f" | Paid via WordPress UPI Gateway (UTR: {utr_number})"
            booking.save()
            request.session['last_payment_utr'] = utr_number

        elif payment_method == 'Cash on Delivery':
            order.fulfillment_status = 'CONFIRMED'
            order.payment_status = 'PENDING'
            order.save(update_fields=['fulfillment_status', 'payment_status', 'updated_at'])
            booking.status = 'Confirmed'
            booking.notes += f" | Cash on Delivery (Total: ₹{payable_amount:,.0f})"
            booking.save()

        else:
            # Card / NetBanking
            gateway_pay_id = f"PAY-{uuid.uuid4().hex[:10].upper()}"
            PaymentTransaction.objects.create(
                order=order,
                gateway=payment_method,
                gateway_payment_id=gateway_pay_id,
                amount=payable_amount,
                currency='INR',
                status='SUCCESS',
                idempotency_key=f"IDEMP-CARD-{order.order_number}-{uuid.uuid4().hex[:6]}",
                paid_at=timezone.now()
            )
            order.recalculate_financials()
        # Keep customer session and order tracking updated
        order_ids = request.session.get('glory_customer_order_ids', [])
        if order.id not in order_ids:
            order_ids.append(order.id)
        request.session['glory_customer_order_ids'] = order_ids
        if order.email:
            request.session['glory_user_email'] = order.email
        if order.customer_name:
            request.session['glory_user_name'] = order.customer_name
        request.session['glory_role'] = 'customer'

        request.session.pop(f'order_payment_{booking.booking_id}', None)
        return redirect('booking_confirmation', booking_id=booking.booking_id)

    context = {
        'booking': booking,
        'order': order,
        'product': order.product,
        'product_name': order.product_name,
        'product_image': order.product.primary_image if order.product else '',
        'selected_size': order.selected_size,
        'selected_wood': order.selected_wood,
        'quantity': order.quantity,
        'total_amount': order.total_amount,
        'paid_amount': order.paid_amount,
        'remaining_amount': order.remaining_amount,
        'payable_amount': payable_amount,
        'formatted_payable': f"₹{int(payable_amount):,}",
        'formatted_total': order.formatted_total,
        'upi_vpa': upi_vpa,
        'payee_name': payee_name,
        'upi_intent_url': upi_intent_url,
        'upi_qr_url': upi_qr_url,
    }
    return render(request, 'bookings/payment.html', context)


def pay_installment_direct_view(request, installment_id):
    """
    Direct payment route when customer clicks [Pay Now] on an installment from My Orders.
    Enforces server-side eligibility check.
    """
    installment = get_object_or_404(Installment, id=installment_id)
    order = installment.order
    booking = order.booking or Booking.objects.filter(email=order.email).first()

    if not installment.is_eligible_for_payment:
        return HttpResponseBadRequest(f"Installment #{installment.installment_number} is not eligible for payment yet.")

    if not booking:
        booking = Booking.objects.create(
            customer_name=order.customer_name,
            email=order.email,
            phone=order.phone,
            consultation_type='Product Order & In-Home Delivery',
            preferred_date=timezone.now().date() + timedelta(days=3),
            address=order.shipping_address,
            status='Payment Pending'
        )
        order.booking = booking
        order.save()

    return redirect(f"/payments/checkout/{order.order_number}/?installment_id={installment.id}")


def booking_view(request):
    """
    Genuine Studio & In-Home Consultation scheduling page.
    Renders templates/bookings/booking.html and processes appointment requests.
    Supports Showroom Visit, In-Home Site Measurement, and Video Consultation.
    """
    # If a product_id was explicitly passed, redirect to checkout summary
    product_id = request.GET.get('productId') or request.GET.get('product')
    if product_id and request.method != 'POST':
        return redirect(f"/booking/summary/?product={product_id}")

    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None

    if request.method == 'POST':
        consultation_type = request.POST.get('consultation_type', 'Showroom Visit')
        preferred_date = request.POST.get('preferred_date') or str(timezone.now().date() + timedelta(days=3))
        time_slot = request.POST.get('time_slot', '11:00 AM - 01:00 PM')
        wood_preference = request.POST.get('wood_preference', 'Royal Burma Teak')
        name = request.POST.get('name', '').strip() or (profile.full_name if profile and profile.full_name else (user.get_full_name() if user else 'Valued Patron'))
        email = request.POST.get('email', '').strip().lower() or (user.email if user else '')
        phone = request.POST.get('phone', '').strip() or (profile.phone if profile and profile.phone else '')
        address = request.POST.get('address', '').strip()
        notes = request.POST.get('notes', '').strip()

        booking = Booking.objects.create(
            customer_name=name,
            email=email,
            phone=phone,
            consultation_type=consultation_type,
            preferred_date=preferred_date,
            time_slot=time_slot,
            wood_preference=wood_preference,
            address=address,
            notes=notes,
            status='Scheduled'
        )

        request.session['last_booking_id'] = booking.booking_id
        return redirect('booking_confirmation', booking_id=booking.booking_id)

    time_slots = [
        '10:00 AM - 12:00 PM',
        '12:00 PM - 02:00 PM',
        '03:00 PM - 05:00 PM',
        '05:00 PM - 07:00 PM',
    ]
    wood_types = [
        'Royal Burma Teak (Grade-A)',
        'Central Province (CP) Teak',
        'Golden Teak with Natural Grains',
        'Dark Walnut Stained Teak',
    ]
    default_date = str(timezone.now().date() + timedelta(days=2))

    context = {
        'time_slots': time_slots,
        'wood_types': wood_types,
        'default_date': default_date,
        'USER_NAME': profile.full_name if profile and profile.full_name else (user.get_full_name() if user else ''),
        'USER_EMAIL': user.email if user else '',
        'USER_PHONE': profile.phone if profile and profile.phone else '',
    }
    return render(request, 'bookings/booking.html', context)


def booking_confirmation_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    order = Order.objects.filter(booking=booking).first()
    utr_number = request.session.get('last_payment_utr')
    if not utr_number and order:
        tx = order.transactions.filter(gateway='WordPress UPI Gateway').last()
        if tx and tx.gateway_payment_id and tx.gateway_payment_id.startswith('UTR-'):
            utr_number = tx.gateway_payment_id.replace('UTR-', '')
    return render(request, 'bookings/booking_confirmation.html', {
        'booking': booking,
        'order': order,
        'utr_number': utr_number,
    })


def my_bookings_view(request):
    """
    Customer Orders: redirects to dedicated customer orders page
    with route identification, processing pending, and delivery confirmation.
    """
    return redirect('orders')


def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    order = Order.objects.filter(booking=booking).first()
    return render(request, 'bookings/booking_detail.html', {'booking': booking, 'order': order})


# =========================================================
# ADMIN INSTALLMENT MANAGEMENT & RESCHEDULING VIEWS
# =========================================================

def _is_admin(request):
    return request.session.get('glory_role') == 'admin' or (request.user.is_authenticated and request.user.is_staff)


def admin_order_detail_view(request, order_id):
    """
    Admin view for an individual customer order:
    Displays Order Summary, Decoupled Financial Status, Payment Ledger,
    5-Stage Workshop Progress, Installment Schedule, Reschedule Audits,
    Manual Payment Verification, and Workshop Status History.
    """
    if not _is_admin(request):
        return HttpResponseForbidden("Access Denied: Admin privileges required.")

    order = get_object_or_404(Order, id=order_id)
    error_message = None

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. Reschedule installment
        if action == 'reschedule_installment':
            inst_id = request.POST.get('installment_id')
            new_due_str = request.POST.get('new_due_date', '').strip()
            reason = request.POST.get('reason', '').strip()
            notify_customer = request.POST.get('notify_customer') == 'on'

            try:
                new_date = datetime.strptime(new_due_str, '%Y-%m-%d').date()
                admin_name = request.session.get('glory_user_name', 'Master Studio Admin')
                RescheduleService.reschedule_installment(
                    installment_id=inst_id,
                    new_due_date=new_date,
                    reason=reason,
                    changed_by=admin_name,
                    notify_customer=notify_customer
                )
                return redirect(f"/admin-portal/order/{order.id}/?success=rescheduled")
            except (ValueError, InstallmentRescheduleError) as err:
                error_message = str(err)

        # 2. Update workshop / fulfillment status
        elif action in ['update_fulfillment_status', 'update_order_status']:
            new_status = request.POST.get('fulfillment_status') or request.POST.get('order_status')
            status_map = {
                'CONFIRMED': 'CONFIRMED',
                'IN_PRODUCTION': 'IN_PRODUCTION',
                'READY_FOR_DELIVERY': 'SHIPPED',
                'SHIPPED': 'SHIPPED',
                'OUT_FOR_DELIVERY': 'OUT_FOR_DELIVERY',
                'DELIVERED': 'DELIVERED',
            }
            mapped_status = status_map.get(new_status, new_status)
            valid_statuses = [s[0] for s in Order.FULFILLMENT_STATUS_CHOICES]

            if mapped_status not in valid_statuses:
                error_message = f"Invalid workshop stage: '{new_status}'. Allowed stages: Confirmed, In Production, Shipped, Out for Delivery, Delivered."
            else:
                override_shipping = request.POST.get('override_shipping_payment') in ['true', 'on', '1']
                override_reason = request.POST.get('override_reason', '').strip()

                if mapped_status == 'SHIPPED' and order.remaining_amount > Decimal('0.00') and not override_shipping:
                    error_message = (
                        f"Warning: Order #{order.order_number} has an unpaid balance of {order.formatted_remaining}. "
                        f"Shipping an unpaid order requires an authorized Admin Override with mandatory justification."
                    )
                else:
                    old_status = order.fulfillment_status
                    order.fulfillment_status = mapped_status
                    order.save(update_fields=['fulfillment_status', 'updated_at'])

                    admin_notes = request.POST.get('admin_notes', '').strip()
                    if override_shipping and mapped_status == 'SHIPPED' and order.remaining_amount > Decimal('0.00'):
                        admin_notes = f"SHIPPING OVERRIDE: {override_reason}. {admin_notes}".strip()
                        OrderAdminAuditLog.objects.create(
                            order=order,
                            action='ADMIN_OVERRIDE',
                            performed_by=request.user if request.user.is_authenticated else None,
                            old_value=old_status,
                            new_value='SHIPPED',
                            notes=f"Overridden shipping payment rule for unpaid balance {order.formatted_remaining}: {override_reason}"
                        )

                    OrderStatusHistory.objects.create(
                        order=order,
                        previous_status=old_status,
                        fulfillment_status=mapped_status,
                        changed_by=request.user if request.user.is_authenticated else None,
                        admin_notes=admin_notes
                    )
                    OrderAdminAuditLog.objects.create(
                        order=order,
                        action='WORKSHOP_STATUS_CHANGED',
                        performed_by=request.user if request.user.is_authenticated else None,
                        old_value=old_status,
                        new_value=mapped_status,
                        notes=admin_notes
                    )
                    return redirect(f"/admin-portal/order/{order.id}/?success=status_updated")

        # 3. Add manual payment
        elif action == 'add_manual_payment':
            amount = request.POST.get('amount')
            payment_method = request.POST.get('payment_method', 'CASH')
            reference_number = request.POST.get('reference_number', '').strip()
            notes = request.POST.get('notes', '').strip()
            installment_id = request.POST.get('installment_id') or None
            auto_verify = request.POST.get('auto_verify') in ['true', 'on', '1']

            try:
                payment = ManualPaymentService.record_manual_payment(
                    order=order,
                    amount=amount,
                    payment_method=payment_method,
                    reference_number=reference_number,
                    installment=int(installment_id) if installment_id else None,
                    notes=notes,
                    admin_user=request.user if request.user.is_authenticated else None
                )
                if auto_verify:
                    ManualPaymentService.verify_manual_payment(
                        payment_id=payment.payment_id,
                        admin_user=request.user if request.user.is_authenticated else None,
                        verification_notes="Auto-verified by admin upon entry"
                    )
                    return redirect(f"/admin-portal/order/{order.id}/?success=payment_verified")
                return redirect(f"/admin-portal/order/{order.id}/?success=payment_recorded")
            except Exception as e:
                error_message = f"Failed to record manual payment: {str(e)}"

        # 4. Verify manual payment
        elif action == 'verify_manual_payment':
            payment_id = request.POST.get('payment_id')
            notes = request.POST.get('notes', '').strip()
            try:
                ManualPaymentService.verify_manual_payment(
                    payment_id=payment_id,
                    admin_user=request.user if request.user.is_authenticated else None,
                    verification_notes=notes
                )
                return redirect(f"/admin-portal/order/{order.id}/?success=payment_verified")
            except Exception as e:
                error_message = f"Verification failed: {str(e)}"

        # 5. Reject manual payment
        elif action == 'reject_manual_payment':
            payment_id = request.POST.get('payment_id')
            reason = request.POST.get('reason', '').strip()
            try:
                ManualPaymentService.reject_manual_payment(
                    payment_id=payment_id,
                    admin_user=request.user if request.user.is_authenticated else None,
                    rejection_reason=reason
                )
                return redirect(f"/admin-portal/order/{order.id}/?success=payment_rejected")
            except Exception as e:
                error_message = f"Rejection failed: {str(e)}"

    order.refresh_from_db()
    installments = order.installments.all().order_by('installment_number')
    audits = order.reschedule_audits.all().order_by('-created_at')
    transactions = order.transactions.all().order_by('-created_at')
    ledger = PaymentLedgerService.get_order_transactions(order)
    status_history = order.status_history.all().order_by('-created_at')
    admin_audit_logs = order.admin_audit_logs.all().order_by('-created_at')
    pending_manual_payments = order.payments.filter(is_manual=True, verification_status='PENDING_VERIFICATION')

    context = {
        'order': order,
        'installments': installments,
        'audits': audits,
        'transactions': transactions,
        'ledger': ledger,
        'status_history': status_history,
        'admin_audit_logs': admin_audit_logs,
        'pending_manual_payments': pending_manual_payments,
        'fulfillment_choices': Order.FULFILLMENT_STATUS_CHOICES,
        'success': request.GET.get('success'),
        'error_message': error_message,
    }
    return render(request, 'admin_portal/order_detail.html', context)


@csrf_exempt
def admin_reschedule_api(request, order_id, installment_id):
    """
    REST API endpoint to reschedule an installment:
    PATCH/POST /api/orders/<order_id>/installments/<installment_id>/reschedule/
    """
    if not _is_admin(request):
        return JsonResponse({'status': 'error', 'message': 'Admin privileges required.'}, status=403)

    if request.method not in ['POST', 'PATCH']:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    new_due_str = data.get('new_due_date')
    reason = data.get('reason')
    notify_customer = bool(data.get('notify_customer', False))

    if not new_due_str:
        return JsonResponse({'status': 'error', 'message': 'new_due_date is required.'}, status=400)
    if not reason:
        return JsonResponse({'status': 'error', 'message': 'reason is required.'}, status=400)

    try:
        new_date = datetime.strptime(new_due_str, '%Y-%m-%d').date()
        admin_name = request.session.get('glory_user_name', 'Master Studio Admin')
        success, audit, msg = RescheduleService.reschedule_installment(
            installment_id=installment_id,
            new_due_date=new_date,
            reason=reason,
            changed_by=admin_name,
            notify_customer=notify_customer
        )
        return JsonResponse({
            'status': 'success',
            'message': msg,
            'audit': {
                'id': audit.id,
                'old_due_date': audit.old_due_date.isoformat(),
                'new_due_date': audit.new_due_date.isoformat(),
                'reason': audit.reason,
                'changed_by': audit.changed_by,
                'customer_notified': audit.customer_notified,
            }
        })
    except (ValueError, InstallmentRescheduleError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# =========================================================
# SECURE PAYMENT WEBHOOK WITH IDEMPOTENCY
# =========================================================

@csrf_exempt
def payment_webhook_api(request):
    """
    Secure webhook endpoint for payment gateways (Razorpay / UPI / Cards).
    Verifies signature and idempotently marks installments/orders as paid.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("Method not allowed")

    secret = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', 'glory-secret-webhook-key-2026')
    signature = request.headers.get('X-Razorpay-Signature') or request.headers.get('X-Webhook-Signature') or ''

    body = request.body
    # Verify HMAC signature if provided
    if signature:
        expected_sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return HttpResponseForbidden("Invalid webhook signature")

    try:
        payload = json.loads(body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON body")

    order_id = payload.get('order_id')
    installment_id = payload.get('installment_id')
    gateway_payment_id = payload.get('gateway_payment_id') or payload.get('payment_id')
    amount = payload.get('amount')
    gateway = payload.get('gateway', 'Razorpay')

    if not order_id or not gateway_payment_id:
        return HttpResponseBadRequest("Missing required order_id or gateway_payment_id")

    order = Order.objects.filter(id=order_id).first() or Order.objects.filter(order_number=order_id).first()
    if not order:
        return HttpResponseBadRequest("Order not found")

    try:
        success, txn, msg = PaymentService.process_payment(
            order=order,
            installment_id=installment_id,
            amount=Decimal(str(amount)) if amount else None,
            gateway=gateway,
            gateway_payment_id=gateway_payment_id,
            idempotency_key=f"WEBHOOK-{gateway_payment_id}"
        )
        return JsonResponse({'status': 'success', 'message': msg, 'transaction_id': txn.id})
    except Exception as e:
        return HttpResponseBadRequest(f"Webhook processing error: {str(e)}")
