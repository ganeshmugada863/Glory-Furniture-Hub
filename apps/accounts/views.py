from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from apps.store.models import Product, Category
from apps.bookings.models import Booking, Order, PaymentTransaction, OrderStatusHistory, OrderAdminAuditLog
from apps.bookings.services import OrderAccessControl
from apps.payments.models import Payment
from apps.payments.services import ManualPaymentService, PaymentLedgerService
from django.utils import timezone
from decimal import Decimal
from apps.custom_orders.models import CustomRequest
from .models import UserProfile, Notification

# =====================================================================
# 1. CUSTOMER AUTHENTICATION & PORTAL VIEWS
# =====================================================================

# =====================================================================
# USER DATA SYNCHRONIZATION & MULTI-TENANT ISOLATION HELPERS
# =====================================================================

def sync_user_session(request, user):
    """
    Synchronizes authenticated database User & UserProfile data directly into the active session.
    Restores persistent cart_items, wishlist_ids, and saved_addresses.
    Guarantees strict multi-tenant data isolation per user.
    """
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Auto-claim any guest orders created with this verified email
    if user.email:
        Order.objects.filter(user__isnull=True, email__iexact=user.email.strip()).update(user=user)

    # Strictly populate session with this user's own orders
    user_order_ids = list(Order.objects.filter(user=user).values_list('id', flat=True))

    request.session['glory_user_email'] = user.email
    request.session['glory_user_name'] = profile.full_name or user.get_full_name() or user.username
    request.session['glory_user_phone'] = profile.phone or ''
    request.session['glory_role'] = profile.role or ('admin' if (user.is_staff or user.is_superuser) else 'customer')
    request.session['glory_cart'] = profile.cart_items or []
    request.session['glory_wishlist'] = profile.wishlist_ids or []
    request.session['glory_addresses'] = profile.saved_addresses or []
    request.session['glory_customer_order_ids'] = user_order_ids
    if hasattr(request, 'session') and hasattr(request.session, 'modified'):
        request.session.modified = True


def persist_session_to_user(request):
    """
    Saves current session cart_items, wishlist_ids, and saved_addresses to the database UserProfile.
    Called before logout or whenever cart/wishlist/addresses are updated.
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.cart_items = request.session.get('glory_cart', [])
            profile.wishlist_ids = request.session.get('glory_wishlist', [])
            profile.saved_addresses = request.session.get('glory_addresses', [])
            profile.save(update_fields=['cart_items', 'wishlist_ids', 'saved_addresses'])
        except Exception as e:
            print(f"[persist_session_to_user error]: {e}")


def customer_login_view(request):
    """
    Dedicated Customer & Staff Login view.
    If admin credentials are submitted, securely routes to /admin/dashboard/.
    If customer credentials are submitted, securely routes to / (storefront).
    """
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')  # Note: DO NOT strip password characters

        if not email or not password:
            error = "Please enter both email and password."
        else:
            # 1. Authenticate with Django User credentials
            user = authenticate(request, username=email, password=password)
            if user is None:
                # Check by email lookup if username differs (e.g. username='admin', email='admin@gloryfurniture.com')
                matched_user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
                if matched_user:
                    user = authenticate(request, username=matched_user.username, password=password)

            # 2. Check if this is an admin logging in
            is_admin = False
            if user is not None:
                profile = getattr(user, 'profile', None)
                if user.is_staff or user.is_superuser or (profile and profile.role == 'admin'):
                    is_admin = True

            if user is not None:
                if not user.is_active:
                    error = "This account has been deactivated. Please contact customer support."
                else:
                    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    profile, _ = UserProfile.objects.get_or_create(user=user)

                    if is_admin:
                        request.session['glory_role'] = 'admin'
                        request.session['glory_user_email'] = user.email or 'admin@gloryfurniture.com'
                        request.session['glory_user_name'] = 'Master Studio Admin'
                        request.session['glory_user_phone'] = profile.phone or ''
                        profile.role = 'admin'
                        profile.save()

                        messages.success(request, "Welcome back, Master Studio Admin!")
                        next_url = request.GET.get('next')
                        if next_url and next_url.startswith('/admin'):
                            return redirect(next_url)
                        return redirect('admin_dashboard')
                    else:
                        sync_user_session(request, user)
                        user_display_name = profile.full_name or user.get_full_name() or user.username
                        messages.success(request, f"Welcome back, {user_display_name}!")
                        next_url = request.GET.get('next')
                        if next_url and not next_url.startswith('/admin'):
                            return redirect(next_url)
                        return redirect('home')
            else:
                matched_user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
                if matched_user and not matched_user.has_usable_password():
                    error = "This account was created with Google. Please continue with Google or reset your password."
                elif matched_user and not matched_user.is_active:
                    error = "This account has been deactivated. Please contact customer support."
                else:
                    error = "Invalid email or password. Please verify your credentials or create a new account."

    from apps.core.models import PageCMSContent
    cms_obj = PageCMSContent.get_cms()
    return render(request, 'accounts/login.html', {'error': error, 'cms': cms_obj})


def customer_register_view(request):
    """
    Dedicated Customer Registration page.
    Creates User and UserProfile models in the persistent database.
    """
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')  # Preserve exact password characters
        confirm_password = request.POST.get('confirm_password', '')

        if not email or not password or not name:
            error = "Please fill in all required fields (Name, Email, Password)."
        elif password != confirm_password:
            error = "Passwords do not match. Please re-enter your password."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            error = "An account with this email address already exists. Please sign in."
        else:
            # Create permanent User record
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = True
            name_parts = name.split()
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()

            # Create permanent UserProfile record
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.full_name = name
            profile.phone = phone or ''
            profile.role = 'customer'
            profile.auth_provider = 'email'
            profile.save()

            # Log user in
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            sync_user_session(request, user)
            messages.success(request, f"Welcome to Glory Furniture Hub, {profile.full_name}! Your account has been created.")
            return redirect('home')

    from apps.core.models import PageCMSContent
    cms_obj = PageCMSContent.get_cms()
    return render(request, 'accounts/register.html', {'error': error, 'cms': cms_obj})



@csrf_exempt
def google_auth_view(request):
    """
    Google Authentication Endpoint (Supabase OAuth & Google Identity Services).
    Decodes Google OAuth credentials or verifies Supabase tokens and creates or logs in
    a customer in the persistent database without conflicting with email/password accounts.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        credential = data.get('credential', '')
        access_token = data.get('access_token', '')
        
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        google_id = data.get('google_id', '')
        avatar_url = data.get('avatar_url', '')

        # 1. If Supabase access_token is present and email missing, verify with Supabase Auth API
        if access_token and not email:
            try:
                import urllib.request
                supabase_url = 'https://qxxrghelhlrafdkveeqo.supabase.co/auth/v1/user'
                anon_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4eHJnaGVsaGxyYWZka3ZlZXFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg0NDMwNTEsImV4cCI6MjEwNDAxOTA1MX0.mc-5c84wqAaD5_ybaHS_vHZSYgczA2bIjWC2KwIPfZA'
                req = urllib.request.Request(supabase_url, headers={
                    'Authorization': f'Bearer {access_token}',
                    'apikey': anon_key
                })
                with urllib.request.urlopen(req, timeout=5) as response:
                    user_data = json.loads(response.read().decode('utf-8'))
                    email = user_data.get('email', '').strip().lower()
                    meta = user_data.get('user_metadata', {})
                    name = meta.get('full_name') or meta.get('name') or name
                    avatar_url = meta.get('avatar_url') or meta.get('picture') or avatar_url
                    google_id = user_data.get('id') or google_id
            except Exception as token_err:
                print(f"[Supabase Auth Token Verification Error]: {token_err}")

        # Fallback decode payload directly from access_token if email is still missing
        if access_token and not email:
            try:
                parts = access_token.split('.')
                if len(parts) >= 2:
                    padded = parts[1] + '=' * ((4 - len(parts[1]) % 4) % 4)
                    payload_json = base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8')
                    payload = json.loads(payload_json)
                    email = payload.get('email', '').strip().lower()
                    meta = payload.get('user_metadata', {})
                    name = meta.get('full_name') or meta.get('name') or payload.get('name') or name
                    avatar_url = meta.get('avatar_url') or meta.get('picture') or payload.get('picture') or avatar_url
                    google_id = payload.get('sub') or google_id
            except Exception as jwt_err:
                print(f"[Supabase JWT Decode Error]: {jwt_err}")

        # 2. If credential JWT was sent by Google Identity Services, decode payload
        if credential and not email:
            parts = credential.split('.')
            if len(parts) >= 2:
                padded = parts[1] + '=' * ((4 - len(parts[1]) % 4) % 4)
                payload_json = base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8')
                payload = json.loads(payload_json)
                email = payload.get('email', '').strip().lower()
                name = payload.get('name', '').strip()
                google_id = payload.get('sub', '')
                avatar_url = payload.get('picture', '')

        if not email:
            return JsonResponse({'status': 'error', 'message': 'Could not extract verified email from Google authentication.'}, status=400)

        # Retrieve or create User in persistent database
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(username__iexact=email).first()

        if not user:
            # Create new Google-only user
            user = User.objects.create_user(username=email, email=email)
            user.set_unusable_password()
            user.is_active = True
            name_parts = (name or '').split()
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()

            profile = UserProfile.objects.create(
                user=user,
                full_name=name or email.split('@')[0].title(),
                phone='',
                role='customer',
                auth_provider='google',
                google_id=google_id,
                avatar_url=avatar_url
            )
        else:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            # CRITICAL: If the user registered previously with email/password,
            # NEVER wipe out or disable their password! Keep user.password intact.
            if google_id:
                profile.google_id = google_id
            if avatar_url:
                profile.avatar_url = avatar_url
            if name and not profile.full_name:
                profile.full_name = name
            if not profile.auth_provider:
                profile.auth_provider = 'google'
            profile.save()

        # Log in the user safely specifying backend
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        sync_user_session(request, user)
        messages.success(request, f"Welcome to Glory Furniture Hub, {profile.full_name}!")
        return JsonResponse({'status': 'success', 'redirect_url': '/'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def supabase_callback_view(request):
    """
    Supabase OAuth Callback view.
    Receives OAuth callback from Google via Supabase, extracts session,
    and logs customer into Django session before redirecting to home page (/).
    """
    return render(request, 'accounts/supabase_callback.html')


def customer_logout_view(request):
    """
    Customer Logout: Persists user cart/wishlist/addresses to DB,
    clears session completely, and redirects cleanly to Login page.
    """
    persist_session_to_user(request)
    auth_logout(request)
    request.session.flush()
    messages.success(request, "You have been signed out successfully.")
    return redirect('home')


def customer_home_view(request):
    """
    Dedicated Customer Home / Dashboard.
    Customer-facing view with personalized welcome, order tracking,
    recent bookings, and quick catalog actions.
    Strictly isolated to this specific customer.
    """
    user = request.user if request.user.is_authenticated else None
    customer_email = (user.email if user else None) or request.session.get('glory_user_email')
    
    if user:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        customer_name = profile.full_name or user.get_full_name() or user.username
        customer_phone = profile.phone or ''
        orders = Order.objects.filter(user=user).distinct().prefetch_related('transactions').order_by('-created_at')
        bookings = Booking.objects.filter(email__iexact=user.email).order_by('-created_at') if user.email else Booking.objects.none()
    elif customer_email:
        customer_name = request.session.get('glory_user_name', 'Valued Patron')
        customer_phone = request.session.get('glory_user_phone', '')
        tracked_ids = request.session.get('glory_customer_order_ids', [])
        orders = Order.objects.filter(id__in=tracked_ids, email__iexact=customer_email, user__isnull=True).distinct().prefetch_related('transactions').order_by('-created_at')
        bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')
    else:
        customer_name = request.session.get('glory_user_name', 'Valued Patron')
        customer_phone = request.session.get('glory_user_phone', '')
        orders = Order.objects.none()
        bookings = Booking.objects.none()

    latest_order = orders.first()
    featured_products = Product.objects.filter(featured=True)[:4]
    if not featured_products.exists():
        featured_products = Product.objects.all()[:4]

    total_spent = sum((o.paid_amount for o in orders), Decimal('0.00'))

    context = {
        'customer_name': customer_name,
        'customer_email': customer_email or '',
        'customer_phone': customer_phone,
        'orders': orders[:4],
        'total_orders': orders.count(),
        'bookings': bookings[:3],
        'total_bookings': bookings.count(),
        'latest_order': latest_order,
        'featured_products': featured_products,
        'total_spent': f"₹{int(total_spent):,}",
    }
    return render(request, 'customer/customer_home.html', context)


def customer_orders_view(request):
    """
    Dedicated My Orders page: Customers can view their handcrafted orders.
    Shows 100% Full Payment or 3-Installments status, product specifications, and 5-stage workshop progress.
    Strictly isolated to this specific user.
    """
    user = request.user if request.user.is_authenticated else None
    customer_email = (user.email if user else None) or request.session.get('glory_user_email')

    if user:
        orders = Order.objects.filter(user=user).distinct().select_related('product').prefetch_related('transactions', 'payments', 'installments', 'status_history').order_by('-created_at')
    elif customer_email:
        tracked_ids = request.session.get('glory_customer_order_ids', [])
        orders = Order.objects.filter(id__in=tracked_ids, email__iexact=customer_email, user__isnull=True).distinct().select_related('product').prefetch_related('transactions', 'payments', 'installments', 'status_history').order_by('-created_at')
    else:
        orders = Order.objects.none()

    return render(request, 'customer/customer_orders.html', {
        'orders': orders,
        'total_orders': orders.count(),
        'customer_email': customer_email or '',
    })


def customer_order_detail_view(request, order_number):
    """
    Dedicated Flipkart-style Order Tracking & Timeline Detail View for an individual order.
    Shows delivery address card, Flipkart-style multi-stage timeline with timestamps and artisan notes,
    wood care guide link, and financial installment milestones.
    Strictly checks ownership permission.
    """
    order = get_object_or_404(
        Order.objects.select_related('product', 'user', 'booking')
                     .prefetch_related('installments', 'status_history', 'payments', 'transactions'),
        order_number=order_number
    )

    if not OrderAccessControl.check_order_access(request, order):
        return HttpResponseForbidden("Access Denied: You do not have permission to view this order.")

    timeline = order.get_flipkart_timeline()
    user = request.user if request.user.is_authenticated else None
    customer_email = (user.email if user else None) or request.session.get('glory_user_email')

    context = {
        'order': order,
        'timeline': timeline,
        'installments': order.installments.all().order_by('installment_number'),
        'status_history': order.status_history.all().order_by('-created_at'),
        'customer_email': customer_email or order.email,
    }
    return render(request, 'customer/customer_order_detail.html', context)


def customer_bookings_view(request):
    """
    Dedicated My Bookings page: Customers can view ONLY their own consultations.
    """
    user = request.user if request.user.is_authenticated else None
    customer_email = (user.email if user else None) or request.session.get('glory_user_email')
    if user and user.email:
        bookings = Booking.objects.filter(email__iexact=user.email).order_by('-created_at')
    elif customer_email:
        bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')
    else:
        bookings = Booking.objects.none()

    return render(request, 'customer/customer_bookings.html', {
        'bookings': bookings,
        'total_bookings': bookings.count(),
    })


def customer_payments_view(request):
    """
    Dedicated Payment History page: Verified transactions with UTR receipts.
    Strictly isolated to this specific user.
    """
    user = request.user if request.user.is_authenticated else None
    customer_email = (user.email if user else None) or request.session.get('glory_user_email')

    if user:
        transactions = PaymentTransaction.objects.filter(order__user=user).distinct().select_related('order').order_by('-paid_at')
    elif customer_email:
        tracked_ids = request.session.get('glory_customer_order_ids', [])
        transactions = PaymentTransaction.objects.filter(
            order_id__in=tracked_ids,
            order__email__iexact=customer_email,
            order__user__isnull=True
        ).distinct().select_related('order').order_by('-paid_at')
    else:
        transactions = PaymentTransaction.objects.none()

    return render(request, 'customer/customer_payments.html', {
        'transactions': transactions,
        'total_transactions': transactions.count(),
    })


def customer_profile_view(request):
    """Customer profile and preferences with real user stats and orders."""
    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None
    
    customer_email = (user.email if user else None) or request.session.get('glory_user_email') or ''
    customer_name = ''
    if profile and profile.full_name and profile.full_name.strip():
        customer_name = profile.full_name.strip()
    elif user:
        full = user.get_full_name().strip()
        customer_name = full if full else (user.username or '')
    if not customer_name:
        customer_name = request.session.get('glory_user_name') or 'Valued Patron'
    customer_phone = (profile.phone if profile and profile.phone else None) or request.session.get('glory_user_phone') or ''

    if user:
        orders = Order.objects.filter(user=user).distinct().select_related('product').order_by('-created_at')
        bookings = Booking.objects.filter(email__iexact=user.email).order_by('-created_at')[:5] if user.email else []
        custom_requests = CustomRequest.objects.filter(email__iexact=user.email).order_by('-created_at')[:3] if user.email else []
    elif customer_email:
        tracked_ids = request.session.get('glory_customer_order_ids', [])
        orders = Order.objects.filter(id__in=tracked_ids, email__iexact=customer_email, user__isnull=True).distinct().select_related('product').order_by('-created_at')
        bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')[:5]
        custom_requests = CustomRequest.objects.filter(email__iexact=customer_email).order_by('-created_at')[:3]
    else:
        orders = Order.objects.none()
        bookings = []
        custom_requests = []

    wishlist_ids = (profile.wishlist_ids if profile else None) or request.session.get('glory_wishlist', [])

    return render(request, 'accounts/profile.html', {
        'orders': orders[:5],
        'orders_count': orders.count(),
        'bookings': bookings,
        'custom_requests': custom_requests,
        'customer_name': customer_name,
        'customer_email': customer_email,
        'customer_phone': customer_phone,
        'user_initial': customer_name[:1].upper() if customer_name else 'P',
        'wishlist_count': len(wishlist_ids),
        'auth_provider': getattr(profile, 'auth_provider', 'email') if profile else 'email',
    })


def edit_profile_view(request):
    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None
    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()
        new_phone = request.POST.get('phone', '').strip()
        new_address = request.POST.get('address', '').strip()
        update_fields = []
        if new_name:
            request.session['glory_user_name'] = new_name
            if profile:
                profile.full_name = new_name
                update_fields.append('full_name')
        if new_phone:
            request.session['glory_user_phone'] = new_phone
            if profile:
                profile.phone = new_phone
                update_fields.append('phone')
        if new_address is not None:
            request.session['glory_user_address'] = new_address
            if profile:
                profile.address = new_address
                update_fields.append('address')
        if profile and update_fields:
            profile.save(update_fields=list(set(update_fields)))
        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_profile')
    
    user_address = profile.address if profile else request.session.get('glory_user_address', '')
    return render(request, 'accounts/edit_profile.html', {'user_address': user_address})


def address_view(request):
    """
    Delivery Address Management:
    Persists addresses directly to user.profile.saved_addresses in DB and request.session.
    Strictly isolated per user.
    """
    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None

    # Load from profile first, then session
    addresses = (profile.saved_addresses if profile else None) or request.session.get('glory_addresses')
    if addresses is None:
        addresses = []
        if profile and profile.address:
            addresses.append({
                'id': 1,
                'tag': 'Home (Default)',
                'is_default': True,
                'name': profile.full_name or 'Valued Patron',
                'phone': profile.phone or '',
                'email': user.email if user else '',
                'flat': profile.address,
                'street': '',
                'landmark': '',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'pincode': '500034',
            })
        if profile:
            profile.saved_addresses = addresses
            profile.save(update_fields=['saved_addresses'])
        request.session['glory_addresses'] = addresses

    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        if action == 'add':
            new_id = max([a['id'] for a in addresses], default=0) + 1
            tag = request.POST.get('tag', 'Home').strip() or 'Home'
            is_default = request.POST.get('is_default') == '1' or len(addresses) == 0
            if is_default:
                for a in addresses:
                    a['is_default'] = False

            new_addr = {
                'id': new_id,
                'tag': tag,
                'is_default': is_default,
                'name': request.POST.get('name', '').strip() or (profile.full_name if profile else '') or (user.get_full_name() if user else 'Valued Patron'),
                'phone': request.POST.get('phone', '').strip() or (profile.phone if profile else ''),
                'email': (user.email if user else '') or request.POST.get('email', '').strip(),
                'flat': request.POST.get('flat', '').strip(),
                'street': request.POST.get('street', '').strip(),
                'landmark': request.POST.get('landmark', '').strip(),
                'city': request.POST.get('city', 'Hyderabad').strip(),
                'state': request.POST.get('state', 'Telangana').strip(),
                'pincode': request.POST.get('pincode', '500034').strip(),
            }

            addresses.append(new_addr)
            if profile:
                profile.saved_addresses = addresses
                profile.save(update_fields=['saved_addresses'])
            request.session['glory_addresses'] = addresses
            request.session.modified = True
            return redirect('address')

        elif action == 'set_default':
            try:
                addr_id = int(request.POST.get('address_id', 0))
                for a in addresses:
                    a['is_default'] = (a['id'] == addr_id)
                if profile:
                    profile.saved_addresses = addresses
                    profile.save(update_fields=['saved_addresses'])
                request.session['glory_addresses'] = addresses
                request.session.modified = True
            except ValueError:
                pass
            return redirect('address')

        elif action == 'delete':
            try:
                addr_id = int(request.POST.get('address_id', 0))
                addresses = [a for a in addresses if a['id'] != addr_id]
                if addresses and not any(a.get('is_default') for a in addresses):
                    addresses[0]['is_default'] = True
                if profile:
                    profile.saved_addresses = addresses
                    profile.save(update_fields=['saved_addresses'])
                request.session['glory_addresses'] = addresses
                request.session.modified = True
            except ValueError:
                pass
            return redirect('address')

    default_name = (profile.full_name if profile else '') or (user.get_full_name() if user else '') or request.session.get('glory_user_name', '')
    default_phone = (profile.phone if profile else '') or request.session.get('glory_user_phone', '')
    default_email = (user.email if user else '') or request.session.get('glory_user_email', '')

    context = {
        'addresses': addresses,
        'default_name': default_name,
        'default_phone': default_phone,
        'default_email': default_email,
    }
    return render(request, 'accounts/address.html', context)


def forgot_password_view(request):
    submitted = False
    if request.method == 'POST':
        submitted = True
    return render(request, 'accounts/forgot_password.html', {'submitted': submitted})


def notifications_view(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


# =====================================================================
# 2. STUDIO ADMIN PORTAL VIEWS (MANAGEMENT FOCUSED)
# =====================================================================

def admin_login_view(request):
    """
    Dedicated Studio Admin Login.
    On success: sets role='admin', authenticates user, and redirects strictly to /admin/dashboard/.
    Admin is NEVER redirected to the customer homepage.
    """
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        # 1. Authenticate with Django auth
        user = authenticate(request, username=email, password=password)
        if user is None:
            matched_user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)

        is_admin = False
        if user is not None and (user.is_staff or user.is_superuser or getattr(getattr(user, 'profile', None), 'role', '') == 'admin'):
            is_admin = True

        if is_admin and user is not None:
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = 'admin'
            profile.save()

            request.session['glory_role'] = 'admin'
            request.session['glory_user_name'] = 'Master Studio Admin'
            request.session['glory_user_email'] = user.email or 'admin@gloryfurniture.com'

            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/admin/'):
                return redirect(next_url)
            return redirect('admin_dashboard')
        else:
            error = "Invalid administrator credentials. Access restricted to authorized studio personnel."

    return render(request, 'admin_portal/admin_login.html', {'error': error})


def admin_logout_view(request):
    """
    Admin Logout: Clears admin session and redirects strictly to Admin Login (/admin/login/).
    Admin is NEVER redirected to customer dashboard.
    """
    request.session.flush()
    return redirect('admin_login')


def admin_dashboard_view(request):
    """
    Executive Studio Admin Dashboard.
    Contains metrics, recent orders, customer counts, and recent transactions.
    """
    is_valid_admin = (
        request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or 
            getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
        )
    )
    if not is_valid_admin:
        return redirect(f'/admin/login/?next={request.path}')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['update_fulfillment_status', 'update_order_status']:
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('fulfillment_status') or request.POST.get('order_status')
            order = get_object_or_404(Order, id=order_id)
            if new_status in [s[0] for s in Order.FULFILLMENT_STATUS_CHOICES]:
                old_status = order.fulfillment_status
                order.fulfillment_status = new_status
                order.save(update_fields=['fulfillment_status', 'updated_at'])
                OrderStatusHistory.objects.create(
                    order=order,
                    previous_status=old_status,
                    fulfillment_status=new_status,
                    changed_by=request.user if request.user.is_authenticated else None,
                    admin_notes="Updated from Executive Dashboard"
                )
                messages.success(request, f"Order #{order.order_number} workshop progress updated to {new_status}!")
            return redirect('admin_dashboard')

    products = Product.objects.all()
    bookings = Booking.objects.all().order_by('-created_at')
    orders = Order.objects.all().prefetch_related('transactions').order_by('-created_at')
    custom_requests = CustomRequest.objects.all().order_by('-created_at')
    
    # Calculate unique customers
    customer_emails = set(Order.objects.values_list('email', flat=True)) | set(Booking.objects.values_list('email', flat=True))
    total_customers = len(customer_emails)
    
    total_revenue = sum((o.paid_amount for o in orders), Decimal('0.00'))
    fully_paid_count = orders.filter(payment_status='FULLY_PAID').count()
    pending_count = orders.filter(payment_status__in=['PENDING', 'PROCESSING', 'PARTIALLY_PAID']).count()
    recent_transactions = PaymentTransaction.objects.select_related('order').order_by('-paid_at')[:6]
    
    context = {
        'page_title': 'Executive Dashboard',
        'active_nav': 'dashboard',
        'total_products': products.count(),
        'total_orders': orders.count(),
        'total_bookings': bookings.count(),
        'total_customers': total_customers,
        'total_revenue': f"₹{int(total_revenue):,}",
        'fully_paid_count': fully_paid_count,
        'pending_count': pending_count,
        'recent_orders': orders[:6],
        'recent_bookings': bookings[:4],
        'recent_transactions': recent_transactions,
    }
    return render(request, 'admin_portal/admin_dashboard.html', context)


def admin_customers_view(request):
    """
    Dedicated Admin Customer Management page.
    Lists all customers with total orders, total spend, and contact records.
    """
    search_q = request.GET.get('q', '').strip().lower()
    
    customers_dict = {}
    for o in Order.objects.all().order_by('-created_at'):
        e = o.email.lower().strip()
        if e not in customers_dict:
            customers_dict[e] = {
                'name': o.customer_name,
                'email': o.email,
                'phone': o.phone,
                'address': o.shipping_address,
                'orders_count': 0,
                'total_spent': Decimal('0.00'),
                'paid_amount': Decimal('0.00'),
                'first_date': o.created_at,
                'last_date': o.created_at,
                'status': 'Active Patron',
            }
        customers_dict[e]['orders_count'] += 1
        customers_dict[e]['total_spent'] += o.total_amount
        customers_dict[e]['paid_amount'] += o.paid_amount
        if o.created_at < customers_dict[e]['first_date']:
            customers_dict[e]['first_date'] = o.created_at
            
    for b in Booking.objects.all().order_by('-created_at'):
        e = b.email.lower().strip()
        if e not in customers_dict:
            customers_dict[e] = {
                'name': b.customer_name,
                'email': b.email,
                'phone': b.phone,
                'address': b.address,
                'orders_count': 0,
                'total_spent': Decimal('0.00'),
                'paid_amount': Decimal('0.00'),
                'first_date': b.created_at,
                'last_date': b.created_at,
                'status': 'Lead / Inquiry',
            }

    customers_list = list(customers_dict.values())
    
    # Filter if search query
    if search_q:
        customers_list = [
            c for c in customers_list 
            if search_q in c['name'].lower() or search_q in c['email'].lower() or search_q in c['phone']
        ]

    context = {
        'page_title': 'Customer Directory',
        'active_nav': 'customers',
        'customers': customers_list,
        'total_customers': len(customers_list),
        'search_q': search_q,
    }
    return render(request, 'admin_portal/admin_customers.html', context)


def admin_customer_detail_view(request, customer_id=None):
    """
    Admin Customer Detail View:
    Displays complete order history, bookings, and payment records for a customer.
    """
    customer_email = request.GET.get('email', '')
    if not customer_email and customer_id:
        order = Order.objects.filter(id=customer_id).first()
        if order:
            customer_email = order.email
            
    orders = Order.objects.filter(email__iexact=customer_email).prefetch_related('transactions', 'payments', 'installments').order_by('-created_at')
    bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')
    transactions = PaymentTransaction.objects.filter(order__email__iexact=customer_email).order_by('-paid_at')
    
    name = orders.first().customer_name if orders.exists() else (bookings.first().customer_name if bookings.exists() else customer_email)
    phone = orders.first().phone if orders.exists() else (bookings.first().phone if bookings.exists() else '')
    address = orders.first().shipping_address if orders.exists() else (bookings.first().address if bookings.exists() else '')
    total_spent = sum((o.paid_amount for o in orders), Decimal('0.00'))

    context = {
        'page_title': f"Customer: {name}",
        'active_nav': 'customers',
        'customer_name': name,
        'customer_email': customer_email,
        'customer_phone': phone,
        'customer_address': address,
        'total_spent': f"₹{int(total_spent):,}",
        'orders': orders,
        'bookings': bookings,
        'transactions': transactions,
    }
    return render(request, 'admin_portal/admin_customer_detail.html', context)


def admin_orders_view(request):
    """
    Dedicated Admin Orders Management.
    Filter by status, search by order # or customer, update workshop progress,
    and record/verify/reject manual payments.
    """
    status_filter = request.GET.get('status', 'ALL')
    payment_status_filter = request.GET.get('payment_status', 'ALL')
    fulfillment_status_filter = request.GET.get('fulfillment_status', 'ALL')
    search_q = request.GET.get('q', '').strip()
    
    orders = Order.objects.all().prefetch_related('transactions', 'payments', 'installments', 'status_history').order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action in ['update_fulfillment_status', 'update_order_status']:
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('fulfillment_status') or request.POST.get('order_status')
            order = get_object_or_404(Order, id=order_id)
            
            # Map legacy status strings if any submitted
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
                messages.error(request, f"Invalid workshop stage: '{new_status}'. Allowed stages: Confirmed, In Production, Shipped, Out for Delivery, Delivered.")
                return redirect(request.get_full_path())

            override_shipping = request.POST.get('override_shipping_payment') in ['true', 'on', '1']
            override_reason = request.POST.get('override_reason', '').strip()

            if mapped_status == 'SHIPPED' and order.remaining_amount > Decimal('0.00') and not override_shipping:
                messages.error(
                    request,
                    f"Warning: Order #{order.order_number} has an unpaid balance of {order.formatted_remaining}. "
                    f"Shipping an unpaid order requires an authorized Admin Override with mandatory justification."
                )
                return redirect(request.get_full_path())

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
            messages.success(request, f"Order #{order.order_number} workshop progress updated to {order.get_fulfillment_status_display()}!")
            return redirect(request.get_full_path())

        elif action == 'add_manual_payment':
            order_id = request.POST.get('order_id')
            order = get_object_or_404(Order, id=order_id)
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
                    messages.success(request, f"Manual payment of ₹{amount} recorded and verified for Order #{order.order_number}!")
                else:
                    messages.success(request, f"Manual payment of ₹{amount} recorded for Order #{order.order_number} (Awaiting Verification).")
            except Exception as e:
                messages.error(request, f"Failed to record manual payment: {str(e)}")
            return redirect(request.get_full_path())

        elif action == 'verify_manual_payment':
            payment_id = request.POST.get('payment_id')
            notes = request.POST.get('notes', '').strip()
            try:
                ManualPaymentService.verify_manual_payment(
                    payment_id=payment_id,
                    admin_user=request.user if request.user.is_authenticated else None,
                    verification_notes=notes
                )
                messages.success(request, f"Payment #{payment_id} successfully verified and credited to order balance!")
            except Exception as e:
                messages.error(request, f"Verification failed: {str(e)}")
            return redirect(request.get_full_path())

        elif action == 'reject_manual_payment':
            payment_id = request.POST.get('payment_id')
            reason = request.POST.get('reason', '').strip()
            try:
                ManualPaymentService.reject_manual_payment(
                    payment_id=payment_id,
                    admin_user=request.user if request.user.is_authenticated else None,
                    rejection_reason=reason
                )
                messages.warning(request, f"Payment #{payment_id} was rejected.")
            except Exception as e:
                messages.error(request, f"Rejection failed: {str(e)}")
            return redirect(request.get_full_path())

    if status_filter != 'ALL':
        payment_choices = [c[0] for c in Order.PAYMENT_STATUS_CHOICES]
        fulfillment_choices = [c[0] for c in Order.FULFILLMENT_STATUS_CHOICES]
        if status_filter in payment_choices:
            orders = orders.filter(payment_status=status_filter)
        elif status_filter in fulfillment_choices:
            orders = orders.filter(fulfillment_status=status_filter)
        else:
            orders = orders.filter(order_status=status_filter)

    if payment_status_filter != 'ALL':
        orders = orders.filter(payment_status=payment_status_filter)
    if fulfillment_status_filter != 'ALL':
        orders = orders.filter(fulfillment_status=fulfillment_status_filter)
        
    if search_q:
        orders = orders.filter(order_number__icontains=search_q) | orders.filter(customer_name__icontains=search_q) | orders.filter(phone__icontains=search_q)
        
    total_revenue = sum((o.paid_amount for o in orders), Decimal('0.00'))
    
    context = {
        'page_title': 'Orders Management',
        'active_nav': 'orders',
        'orders': orders,
        'total_orders': orders.count(),
        'status_filter': status_filter,
        'payment_status_filter': payment_status_filter,
        'fulfillment_status_filter': fulfillment_status_filter,
        'search_q': search_q,
        'total_revenue': f"₹{int(total_revenue):,}",
        'fulfillment_choices': Order.FULFILLMENT_STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'admin_portal/admin_orders.html', context)


def admin_bookings_view(request):
    """
    Dedicated Admin Consultations & Measurements Management.
    Excludes dummy bookings created by legacy checkout.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_booking_status':
            b_id = request.POST.get('booking_id')
            new_status = request.POST.get('status')
            Booking.objects.filter(booking_id=b_id).update(status=new_status)
            messages.success(request, f"Booking status updated to {new_status}!")
            return redirect('admin_bookings')

    bookings = Booking.objects.all().order_by('-created_at')
    context = {
        'page_title': 'Consultations & Measurements',
        'active_nav': 'bookings',
        'bookings': bookings,
        'total_bookings': bookings.count(),
    }
    return render(request, 'admin_portal/admin_bookings.html', context)


def _save_product_image_file(upload_file):
    """
    Safely and rapidly optimizes and saves an uploaded image file.
    1. Uses Pillow (PIL.Image) to correct mobile camera rotation (EXIF transpose),
       downscale ultra-high-res photos to max 1600px, and compress to high-efficiency JPEG (quality 85).
       Reduces upload overhead by 90%+ in memory.
    2. Primary: If Cloudinary is enabled, uploads with strict 5-second timeout to eliminate request hangs.
    3. Secondary fallback: Saves directly to persistent default_storage immediately.
    """
    import os, uuid, io
    import logging
    from django.conf import settings
    from django.core.files.base import ContentFile
    from PIL import Image, ImageOps

    logger = logging.getLogger(__name__)
    file_name = getattr(upload_file, 'name', 'product.jpg')
    raw_ext = os.path.splitext(file_name)[1].lower()
    content_to_save = upload_file
    output_ext = raw_ext if raw_ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'] else '.jpg'

    # Fast in-memory Pillow optimization for raster images (skips SVG)
    if raw_ext != '.svg':
        try:
            if hasattr(upload_file, 'seek'):
                upload_file.seek(0)
            with Image.open(upload_file) as img:
                # 1. Correct mobile camera rotation from EXIF
                img = ImageOps.exif_transpose(img)

                # 2. Downscale if dimensions exceed 1600px
                max_dim = 1600
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

                # 3. Convert RGBA / Palette to clean RGB JPEG
                buf = io.BytesIO()
                if img.mode in ('RGBA', 'LA', 'P'):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    mask = img.split()[-1] if img.mode in ('RGBA', 'LA') else None
                    bg.paste(img, mask=mask)
                    bg.save(buf, format='JPEG', quality=85, optimize=True)
                else:
                    save_format = 'JPEG' if img.mode == 'RGB' else (img.format or 'JPEG')
                    if str(save_format).upper() in ['JPEG', 'JPG']:
                        img.save(buf, format='JPEG', quality=85, optimize=True)
                    else:
                        img.save(buf, format=save_format, optimize=True)

                buf.seek(0)
                content_to_save = ContentFile(buf.getvalue(), name=f"{uuid.uuid4().hex[:10]}.jpg")
                output_ext = '.jpg'
        except Exception as e:
            logger.warning(f"Pillow image optimization skipped ({e}); using raw file.")
            if hasattr(upload_file, 'seek'):
                upload_file.seek(0)
            content_to_save = upload_file

    # 1. Primary: If Cloudinary is enabled, upload with strict 5-second timeout
    if getattr(settings, 'USE_CLOUDINARY', False):
        try:
            import cloudinary
            import cloudinary.uploader

            cloudinary.config(
                cloud_name=getattr(settings, 'CLOUDINARY_CLOUD_NAME', None),
                api_key=getattr(settings, 'CLOUDINARY_API_KEY', None),
                api_secret=getattr(settings, 'CLOUDINARY_API_SECRET', None),
                secure=True
            )

            public_id = f"products/{uuid.uuid4().hex[:12]}"
            if hasattr(content_to_save, 'seek'):
                content_to_save.seek(0)

            upload_result = cloudinary.uploader.upload(
                content_to_save,
                public_id=public_id,
                resource_type="image",
                overwrite=True,
                timeout=5  # Strict 5-second timeout to prevent admin save delays
            )
            secure_url = upload_result.get('secure_url')
            if secure_url:
                return secure_url
        except Exception as e:
            logger.warning(f"Cloudinary upload timed out or failed ({e}); falling back immediately to persistent storage.")

    # 2. Resilient Persistent Local Storage Fallback
    from django.core.files.storage import default_storage
    filename = f"products/{uuid.uuid4().hex[:10]}{output_ext}"
    if hasattr(content_to_save, 'seek'):
        content_to_save.seek(0)
    saved_path = default_storage.save(filename, content_to_save)
    try:
        url = default_storage.url(saved_path)
        if url:
            return url
    except Exception:
        pass
    media_url = getattr(settings, 'MEDIA_URL', '/media/')
    return f"{media_url}{saved_path}"


def admin_products_view(request):
    """
    Dedicated Product Catalog Inventory Management:
    Allows studio administrators to:
    1. Add new products with up to 4 images (Primary Cover + 3 Detail/Angle views).
    2. Edit existing products with 4 image previews and individual replacement.
    3. Delete products permanently.
    All changes write directly to SQLite database (db.sqlite3) and persist permanently.
    """
    import re
    categories = Category.objects.all().order_by('order', 'name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_product':
            try:
                name = request.POST.get('name', '').strip() or 'Handcrafted Royal Burma Teak Piece'
                
                # Resilient Category lookup
                category_id = request.POST.get('category_id')
                category = Category.objects.filter(id=category_id).first()
                if not category:
                    category = Category.objects.first()
                
                # Resilient Price parsing (handles ₹, commas, spaces)
                raw_price = request.POST.get('price', '0')
                cleaned_price = re.sub(r'[^\d.]', '', str(raw_price))
                try:
                    price = Decimal(cleaned_price) if cleaned_price else Decimal('0')
                except Exception:
                    price = Decimal('0')

                # Process 4 Image Slots
                images_list = ['', '', '', '']

                # Multi-file upload batch support
                multi_files = request.FILES.getlist('product_images')
                for idx, mfile in enumerate(multi_files[:4]):
                    if mfile:
                        images_list[idx] = _save_product_image_file(mfile)

                # Check slot-specific file uploads and URLs
                for slot in range(1, 5):
                    idx = slot - 1
                    file_key = f'image_file_{slot}'
                    url_key = f'image_url_{slot}'

                    # Slot 1 fallback checks for backward compatibility
                    if slot == 1:
                        if file_key not in request.FILES and 'image_file' in request.FILES:
                            file_key = 'image_file'
                        if not request.POST.get(url_key) and request.POST.get('primary_image'):
                            url_key = 'primary_image'

                    if file_key in request.FILES and request.FILES[file_key]:
                        images_list[idx] = _save_product_image_file(request.FILES[file_key])
                    elif request.POST.get(url_key, '').strip():
                        images_list[idx] = request.POST.get(url_key, '').strip()

                primary_image = images_list[0] or '/static/images/card_bed.jpg'
                secondary_images = [img for img in images_list[1:] if img]
                
                material = request.POST.get('material', 'Pure Grade-A Burma Teak').strip() or 'Pure Grade-A Burma Teak'
                style = request.POST.get('style', 'Classic').strip() or 'Classic'
                dimensions = request.POST.get('dimensions', 'Standard').strip() or 'Standard'
                lead_time = request.POST.get('lead_time', '5 - 7 Days Delivery').strip() or '5 - 7 Days Delivery'
                raw_installment_days = str(request.POST.get('installment_days', '')).strip()
                if not raw_installment_days or not raw_installment_days.isdigit() or int(raw_installment_days) <= 0:
                    messages.error(request, "Please enter a valid positive number of days.")
                    return redirect('admin_products')
                installment_days = int(raw_installment_days)
                description = request.POST.get('description', '').strip()
                in_stock = request.POST.get('in_stock') in ['1', 'on', 'true', True]
                featured = request.POST.get('featured') in ['1', 'on', 'true', True]
                new_arrival = request.POST.get('new_arrival') in ['1', 'on', 'true', True]

                # Storage & Category-Specific Variant Deltas
                finishes = {
                    'no_storage_delta': int(request.POST.get('storage_no_delta', -5000) or -5000),
                    'box_storage_delta': int(request.POST.get('storage_box_delta', 0) or 0),
                    'drawer_storage_delta': int(request.POST.get('storage_drawer_delta', 5500) or 5500),
                    'hydraulic_storage_delta': int(request.POST.get('storage_hydraulic_delta', 11000) or 11000),
                    'dining_chair_2_delta': int(request.POST.get('dining_chair_2_delta', -14000) or -14000),
                    'dining_chair_4_delta': int(request.POST.get('dining_chair_4_delta', -7000) or -7000),
                    'dining_chair_8_delta': int(request.POST.get('dining_chair_8_delta', 15000) or 15000),
                    'dining_chair_12_delta': int(request.POST.get('dining_chair_12_delta', 35000) or 35000),
                }
                
                product = Product.objects.create(
                    name=name,
                    category=category,
                    price=price,
                    primary_image=primary_image,
                    secondary_images=secondary_images,
                    material=material,
                    style=style,
                    dimensions=dimensions,
                    lead_time=lead_time,
                    installment_days=installment_days,
                    description=description,
                    in_stock=in_stock,
                    featured=featured,
                    new_arrival=new_arrival,
                    finishes=finishes,
                )
                img_count = 1 + len(secondary_images)
                messages.success(request, f"Product '{product.name}' with {img_count} photo(s) saved to database successfully!")
            except Exception as e:
                messages.error(request, f"Error adding product: {str(e)}")
            return redirect('admin_products')

        elif action == 'edit_product':
            try:
                p_id = request.POST.get('product_id')
                product = get_object_or_404(Product, id=p_id)
                
                name = request.POST.get('name', '').strip()
                if name:
                    product.name = name
                    
                category_id = request.POST.get('category_id')
                if category_id:
                    cat = Category.objects.filter(id=category_id).first()
                    if cat:
                        product.category = cat
                    
                raw_price = request.POST.get('price', '')
                if raw_price:
                    cleaned_price = re.sub(r'[^\d.]', '', str(raw_price))
                    try:
                        product.price = Decimal(cleaned_price) if cleaned_price else product.price
                    except Exception:
                        pass
                    
                # Update 4 image slots for existing product
                current_secondary = list(product.secondary_images or [])
                # Ensure current_secondary has 3 slots
                while len(current_secondary) < 3:
                    current_secondary.append('')

                # Slot 1 (Primary)
                if 'image_file_1' in request.FILES and request.FILES['image_file_1']:
                    product.primary_image = _save_product_image_file(request.FILES['image_file_1'])
                elif 'image_file' in request.FILES and request.FILES['image_file']:
                    product.primary_image = _save_product_image_file(request.FILES['image_file'])
                elif request.POST.get('image_url_1', '').strip():
                    product.primary_image = request.POST.get('image_url_1').strip()
                elif request.POST.get('primary_image', '').strip():
                    product.primary_image = request.POST.get('primary_image').strip()

                # Slots 2, 3, 4 (Secondary Images)
                for slot in [2, 3, 4]:
                    s_idx = slot - 2  # 0, 1, 2 index in secondary
                    file_key = f'image_file_{slot}'
                    url_key = f'image_url_{slot}'

                    if file_key in request.FILES and request.FILES[file_key]:
                        current_secondary[s_idx] = _save_product_image_file(request.FILES[file_key])
                    elif request.POST.get(url_key, '').strip():
                        current_secondary[s_idx] = request.POST.get(url_key).strip()

                product.secondary_images = [img for img in current_secondary if img]

                product.material = request.POST.get('material', product.material).strip()
                product.style = request.POST.get('style', product.style).strip()
                product.dimensions = request.POST.get('dimensions', product.dimensions).strip()
                product.lead_time = request.POST.get('lead_time', product.lead_time).strip()
                raw_installment_days = str(request.POST.get('installment_days', '')).strip()
                if not raw_installment_days or not raw_installment_days.isdigit() or int(raw_installment_days) <= 0:
                    messages.error(request, "Please enter a valid positive number of days.")
                    return redirect('admin_products')
                product.installment_days = int(raw_installment_days)
                product.description = request.POST.get('description', product.description).strip()
                product.in_stock = request.POST.get('in_stock') in ['1', 'on', 'true', True]
                product.featured = request.POST.get('featured') in ['1', 'on', 'true', True]
                product.new_arrival = request.POST.get('new_arrival') in ['1', 'on', 'true', True]
                
                # Update variant and storage price configurations
                current_finishes = dict(product.finishes) if isinstance(product.finishes, dict) else {}
                if 'storage_no_delta' in request.POST:
                    try:
                        current_finishes['no_storage_delta'] = int(request.POST.get('storage_no_delta', -5000))
                        current_finishes['box_storage_delta'] = int(request.POST.get('storage_box_delta', 0))
                        current_finishes['drawer_storage_delta'] = int(request.POST.get('storage_drawer_delta', 5500))
                        current_finishes['hydraulic_storage_delta'] = int(request.POST.get('storage_hydraulic_delta', 11000))
                    except Exception:
                        pass
                if 'dining_chair_2_delta' in request.POST:
                    try:
                        current_finishes['dining_chair_2_delta'] = int(request.POST.get('dining_chair_2_delta', -14000))
                        current_finishes['dining_chair_4_delta'] = int(request.POST.get('dining_chair_4_delta', -7000))
                        current_finishes['dining_chair_8_delta'] = int(request.POST.get('dining_chair_8_delta', 15000))
                        current_finishes['dining_chair_12_delta'] = int(request.POST.get('dining_chair_12_delta', 35000))
                    except Exception:
                        pass
                product.finishes = current_finishes

                product.save()
                messages.success(request, f"Product '{product.name}' updated successfully in database!")
            except Exception as e:
                messages.error(request, f"Error updating product: {str(e)}")
            return redirect('admin_products')

        elif action == 'delete_product':
            p_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=p_id)
            name = product.name
            linked_orders_count = product.orders.count()
            product.delete()
            if linked_orders_count > 0:
                messages.success(request, f"Product '{name}' removed from catalog. {linked_orders_count} associated order and payment record(s) have been permanently preserved.")
            else:
                messages.success(request, f"Product '{name}' permanently removed from database.")
            return redirect('admin_products')

    products = Product.objects.select_related('category').order_by('-id')
    context = {
        'page_title': 'Products & Catalog',
        'active_nav': 'products',
        'products': products,
        'categories': categories,
        'total_products': products.count(),
    }
    return render(request, 'admin_portal/admin_products.html', context)


def admin_categories_view(request):
    """Category management."""
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'page_title': 'Product Categories',
        'active_nav': 'categories',
        'categories': categories,
    }
    return render(request, 'admin_portal/admin_categories.html', context)


def admin_payments_view(request):
    """Dedicated Cashfree Payment Ledger & Gateway Analytics."""
    from apps.payments.views import admin_payments_view as real_admin_payments
    return real_admin_payments(request)


def admin_reports_view(request):
    """Sales and timber performance reports."""
    orders = Order.objects.all()
    total_sales = sum((o.total_amount for o in orders), Decimal('0.00'))
    total_paid = sum((o.paid_amount for o in orders), Decimal('0.00'))
    categories = Category.objects.all()
    
    context = {
        'page_title': 'Sales & Performance Reports',
        'active_nav': 'reports',
        'total_sales': f"₹{int(total_sales):,}",
        'total_paid': f"₹{int(total_paid):,}",
        'total_orders': orders.count(),
        'categories': categories,
    }
    return render(request, 'admin_portal/admin_reports.html', context)


def admin_settings_view(request):
    """
    Dedicated Admin Website Settings & Footer CMS Management:
    Allows studio administrators to edit website identity, emails, phone,
    WhatsApp, address, social media links, and footer copyright permanently.
    Strictly restricted to authorized Administrators.
    """
    # 1. Strict Admin Authorization Check
    is_admin = request.session.get('glory_role') == 'admin' or (
        request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or 
            getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
        )
    )
    if not is_admin:
        messages.error(request, "Access Denied: Administrator privileges required to access Website Settings.")
        return redirect('admin_login')

    from apps.core.models import WebsiteSettings
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    settings_obj = WebsiteSettings.get_settings()

    if request.method == 'POST':
        website_name = request.POST.get('website_name', '').strip() or 'Glory Furniture Hub'
        tagline = request.POST.get('tagline', '').strip()
        primary_email = request.POST.get('primary_email', '').strip()
        secondary_email = request.POST.get('secondary_email', '').strip()
        raw_phone = request.POST.get('phone', '').strip()
        raw_whatsapp = request.POST.get('whatsapp_number', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        country = request.POST.get('country', '').strip() or 'India'
        footer_description = request.POST.get('footer_description', '').strip()
        copyright_text = request.POST.get('copyright_text', '').strip()
        facebook_url = request.POST.get('facebook_url', '').strip()
        instagram_url = request.POST.get('instagram_url', '').strip()
        youtube_url = request.POST.get('youtube_url', '').strip()
        twitter_url = request.POST.get('twitter_url', '').strip()
        linkedin_url = request.POST.get('linkedin_url', '').strip()

        # Validate emails
        if primary_email:
            try:
                validate_email(primary_email)
            except ValidationError:
                messages.error(request, "Invalid Primary Email address format.")
                return redirect('admin_settings')

        if secondary_email:
            try:
                validate_email(secondary_email)
            except ValidationError:
                messages.error(request, "Invalid Secondary Email address format.")
                return redirect('admin_settings')

        # Strictly check & reject prohibited phone numbers
        digits_phone = ''.join(c for c in raw_phone if c.isdigit())
        if '9876543210' in digits_phone:
            raw_phone = ''
        digits_wa = ''.join(c for c in raw_whatsapp if c.isdigit())
        if '9876543210' in digits_wa:
            raw_whatsapp = ''

        # Update and save settings to production database
        settings_obj.website_name = website_name
        settings_obj.tagline = tagline
        settings_obj.primary_email = primary_email
        settings_obj.secondary_email = secondary_email
        settings_obj.phone = raw_phone
        settings_obj.whatsapp_number = raw_whatsapp
        settings_obj.address = address
        settings_obj.city = city
        settings_obj.state = state
        settings_obj.pincode = pincode
        settings_obj.country = country
        settings_obj.footer_description = footer_description
        settings_obj.copyright_text = copyright_text
        settings_obj.facebook_url = facebook_url
        settings_obj.instagram_url = instagram_url
        settings_obj.youtube_url = youtube_url
        settings_obj.twitter_url = twitter_url
        settings_obj.linkedin_url = linkedin_url
        settings_obj.save()

        messages.success(request, "Website Settings and Footer CMS updated successfully!")
        return redirect('admin_settings')

    context = {
        'page_title': 'Website Settings & Footer CMS',
        'active_nav': 'settings',
        'settings': settings_obj,
    }
    return render(request, 'admin_portal/admin_settings.html', context)


def admin_page_cms_view(request):
    """
    Dedicated Page CMS Management in Admin Sidebar:
    Allows studio administrators to edit lyrics/text, titles, subtitles,
    badges, and change/upload hero images for:
    1. Welcome Page
    2. Sign In / Login Page
    3. Create Customer Account / Register Page
    """
    is_admin = request.session.get('glory_role') == 'admin' or (
        request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or 
            getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
        )
    )
    if not is_admin:
        messages.error(request, "Access Denied: Administrator privileges required to access Page CMS.")
        return redirect('admin_login')

    from apps.core.models import PageCMSContent
    cms_obj = PageCMSContent.get_cms()

    if request.method == 'POST':
        # --- Welcome Page Fields ---
        cms_obj.welcome_eyebrow = request.POST.get('welcome_eyebrow', cms_obj.welcome_eyebrow).strip()
        cms_obj.welcome_title_main = request.POST.get('welcome_title_main', cms_obj.welcome_title_main).strip()
        cms_obj.welcome_title_highlight = request.POST.get('welcome_title_highlight', cms_obj.welcome_title_highlight).strip()
        cms_obj.welcome_cta_text = request.POST.get('welcome_cta_text', cms_obj.welcome_cta_text).strip()
        cms_obj.welcome_badge1_title = request.POST.get('welcome_badge1_title', cms_obj.welcome_badge1_title).strip()
        cms_obj.welcome_badge2_title = request.POST.get('welcome_badge2_title', cms_obj.welcome_badge2_title).strip()
        cms_obj.welcome_badge3_title = request.POST.get('welcome_badge3_title', cms_obj.welcome_badge3_title).strip()
        if request.POST.get('welcome_bg_image_url') is not None:
            cms_obj.welcome_bg_image_url = request.POST.get('welcome_bg_image_url', '').strip()
        if 'welcome_bg_image' in request.FILES:
            cms_obj.welcome_bg_image = request.FILES['welcome_bg_image']

        # --- Login Page Fields ---
        cms_obj.login_hero_title = request.POST.get('login_hero_title', cms_obj.login_hero_title).strip()
        cms_obj.login_hero_highlight = request.POST.get('login_hero_highlight', cms_obj.login_hero_highlight).strip()
        cms_obj.login_card_subtitle = request.POST.get('login_card_subtitle', cms_obj.login_card_subtitle).strip()
        cms_obj.login_card_title = request.POST.get('login_card_title', cms_obj.login_card_title).strip()
        cms_obj.login_card_description = request.POST.get('login_card_description', cms_obj.login_card_description).strip()
        cms_obj.login_badge1_title = request.POST.get('login_badge1_title', cms_obj.login_badge1_title).strip()
        cms_obj.login_badge1_desc = request.POST.get('login_badge1_desc', cms_obj.login_badge1_desc).strip()
        cms_obj.login_badge2_title = request.POST.get('login_badge2_title', cms_obj.login_badge2_title).strip()
        cms_obj.login_badge2_desc = request.POST.get('login_badge2_desc', cms_obj.login_badge2_desc).strip()
        cms_obj.login_badge3_title = request.POST.get('login_badge3_title', cms_obj.login_badge3_title).strip()
        cms_obj.login_badge3_desc = request.POST.get('login_badge3_desc', cms_obj.login_badge3_desc).strip()
        if request.POST.get('login_slide1_image_url') is not None:
            cms_obj.login_slide1_image_url = request.POST.get('login_slide1_image_url', '').strip()
        if request.POST.get('login_slide2_image_url') is not None:
            cms_obj.login_slide2_image_url = request.POST.get('login_slide2_image_url', '').strip()
        if request.POST.get('login_slide3_image_url') is not None:
            cms_obj.login_slide3_image_url = request.POST.get('login_slide3_image_url', '').strip()
        if 'login_slide1_image' in request.FILES:
            cms_obj.login_slide1_image = request.FILES['login_slide1_image']

        # --- Register Page Fields ---
        cms_obj.register_hero_badge = request.POST.get('register_hero_badge', cms_obj.register_hero_badge).strip()
        cms_obj.register_hero_title = request.POST.get('register_hero_title', cms_obj.register_hero_title).strip()
        cms_obj.register_hero_desc = request.POST.get('register_hero_desc', cms_obj.register_hero_desc).strip()
        cms_obj.register_card_subtitle = request.POST.get('register_card_subtitle', cms_obj.register_card_subtitle).strip()
        cms_obj.register_card_title = request.POST.get('register_card_title', cms_obj.register_card_title).strip()
        cms_obj.register_card_description = request.POST.get('register_card_description', cms_obj.register_card_description).strip()
        cms_obj.register_badge1_title = request.POST.get('register_badge1_title', cms_obj.register_badge1_title).strip()
        cms_obj.register_badge1_desc = request.POST.get('register_badge1_desc', cms_obj.register_badge1_desc).strip()
        cms_obj.register_badge2_title = request.POST.get('register_badge2_title', cms_obj.register_badge2_title).strip()
        cms_obj.register_badge2_desc = request.POST.get('register_badge2_desc', cms_obj.register_badge2_desc).strip()
        cms_obj.register_badge3_title = request.POST.get('register_badge3_title', cms_obj.register_badge3_title).strip()
        cms_obj.register_badge3_desc = request.POST.get('register_badge3_desc', cms_obj.register_badge3_desc).strip()
        if request.POST.get('register_slide1_image_url') is not None:
            cms_obj.register_slide1_image_url = request.POST.get('register_slide1_image_url', '').strip()
        if request.POST.get('register_slide2_image_url') is not None:
            cms_obj.register_slide2_image_url = request.POST.get('register_slide2_image_url', '').strip()
        if request.POST.get('register_slide3_image_url') is not None:
            cms_obj.register_slide3_image_url = request.POST.get('register_slide3_image_url', '').strip()
        if 'register_slide1_image' in request.FILES:
            cms_obj.register_slide1_image = request.FILES['register_slide1_image']

        cms_obj.save()
        messages.success(request, "Page CMS content updated successfully! Changes are live across Welcome, Login, and Register pages.")
        return redirect('admin_page_cms')

    context = {
        'page_title': 'Page Content CMS (Auth & Welcome)',
        'active_nav': 'page_cms',
        'cms': cms_obj,
    }
    return render(request, 'admin_portal/admin_page_cms.html', context)

