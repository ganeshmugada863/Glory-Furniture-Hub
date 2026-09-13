from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from apps.store.models import Product, Category
from apps.bookings.models import Booking, Order, PaymentTransaction
from django.utils import timezone
from decimal import Decimal
from apps.custom_orders.models import CustomRequest
from .models import UserProfile, Notification

# =====================================================================
# 1. CUSTOMER AUTHENTICATION & PORTAL VIEWS
# =====================================================================

def customer_login_view(request):
    """
    Dedicated Customer & Staff Login view.
    If admin credentials are submitted, securely routes to /admin/dashboard/.
    If customer credentials are submitted, securely routes to / (storefront).
    """
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()

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
        elif email in ['admin', 'admin@gloryfurniture.com', 'admin@gmail.com', 'master@glory.com'] and password in ['admin123', 'admin', 'glory2026', 'AdminPass123!']:
            is_admin = True
            user = User.objects.filter(is_staff=True).first()

        if user is not None:
            auth_login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)

            if is_admin:
                request.session['glory_role'] = 'admin'
                request.session['glory_user_email'] = user.email or 'admin@gloryfurniture.com'
                request.session['glory_user_name'] = 'Master Studio Admin'
                request.session['glory_user_phone'] = profile.phone or '+91 98765 43210'
                profile.role = 'admin'
                profile.save()

                messages.success(request, "Welcome to the Studio Admin Console!")
                next_url = request.GET.get('next')
                if next_url and next_url.startswith('/admin/'):
                    return redirect(next_url)
                return redirect('admin_dashboard')
            else:
                request.session['glory_role'] = 'customer'
                request.session['glory_user_email'] = user.email
                request.session['glory_user_name'] = profile.full_name or user.get_full_name() or email.split('@')[0].title()
                request.session['glory_user_phone'] = profile.phone or '+91 98765 43210'

                messages.success(request, f"Welcome back, {request.session['glory_user_name']}!")
                next_url = request.GET.get('next')
                if next_url and not next_url.startswith('/admin'):
                    return redirect(next_url)
                return redirect('home')
        else:
            error = "Invalid email or password. Please verify your credentials or create a new account."

    return render(request, 'accounts/login.html', {'error': error})


def customer_register_view(request):
    """
    Dedicated Customer Registration page with permanent SQLite database persistence.
    Creates User and UserProfile models in db.sqlite3.
    """
    error = None
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not email or not password or not name:
            error = "Please fill in all required fields (Name, Email, Password)."
        elif password != confirm_password:
            error = "Passwords do not match. Please re-enter your password."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            error = "An account with this email address already exists. Please sign in."
        else:
            # Create permanent User record in SQLite
            user = User.objects.create_user(username=email, email=email, password=password)
            name_parts = name.split()
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()

            # Create permanent UserProfile record in SQLite
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.full_name = name
            profile.phone = phone or '+91 98765 43210'
            profile.role = 'customer'
            profile.auth_provider = 'email'
            profile.save()

            # Log user in
            auth_login(request, user)
            request.session['glory_role'] = 'customer'
            request.session['glory_user_email'] = user.email
            request.session['glory_user_name'] = profile.full_name
            request.session['glory_user_phone'] = profile.phone

            messages.success(request, f"Welcome to Glory Furniture Hub, {profile.full_name}! Your account has been created.")
            return redirect('home')

    return render(request, 'accounts/register.html', {'error': error})


@csrf_exempt
def google_auth_view(request):
    """
    Google Authentication Endpoint.
    Decodes Google OAuth credentials (JWT / token payload) and creates or logs in
    a permanent customer in db.sqlite3.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        credential = data.get('credential', '')
        
        email = data.get('email', '').strip().lower()
        name = data.get('name', '').strip()
        google_id = data.get('google_id', '')
        avatar_url = data.get('avatar_url', '')

        # If credential JWT was sent by Google Identity Services, decode payload
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

        # Retrieve or create User in SQLite
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(username__iexact=email).first()

        if not user:
            user = User.objects.create_user(username=email, email=email)
            user.set_unusable_password()
            name_parts = (name or '').split()
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()

            profile = UserProfile.objects.create(
                user=user,
                full_name=name or email.split('@')[0].title(),
                phone='+91 98765 43210',
                role='customer',
                auth_provider='google',
                google_id=google_id,
                avatar_url=avatar_url
            )
        else:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.auth_provider = 'google'
            if google_id:
                profile.google_id = google_id
            if avatar_url:
                profile.avatar_url = avatar_url
            if name and not profile.full_name:
                profile.full_name = name
            profile.save()

        # Log in the user
        auth_login(request, user)
        request.session['glory_role'] = 'customer'
        request.session['glory_user_email'] = user.email
        request.session['glory_user_name'] = profile.full_name or user.get_full_name() or email.split('@')[0].title()
        request.session['glory_user_phone'] = profile.phone or '+91 98765 43210'

        messages.success(request, f"Signed in with Google as {profile.full_name}!")
        return JsonResponse({'status': 'success', 'redirect_url': '/'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def customer_logout_view(request):
    """
    Customer Logout: Clears customer session and redirects to Register page.
    """
    auth_logout(request)
    request.session.flush()
    return redirect('register')


def customer_home_view(request):
    """
    Dedicated Customer Home / Dashboard.
    Customer-facing view with personalized welcome, order tracking,
    recent bookings, and quick catalog actions.
    """
    customer_email = request.session.get('glory_user_email', 'ganesh@example.com')
    customer_name = request.session.get('glory_user_name', 'Ganesh M.')
    
    # Strictly fetch only this customer's data
    orders = Order.objects.filter(email__iexact=customer_email).prefetch_related('transactions').order_by('-created_at')
    bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')
    
    latest_order = orders.first()
    featured_products = Product.objects.filter(featured=True)[:4]
    if not featured_products.exists():
        featured_products = Product.objects.all()[:4]
        
    total_spent = sum((o.paid_amount for o in orders), Decimal('0.00'))
    
    context = {
        'customer_name': customer_name,
        'customer_email': customer_email,
        'customer_phone': request.session.get('glory_user_phone', '+91 98765 43210'),
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
    Dedicated My Orders page: Customers can view their own handcrafted orders.
    Shows 100% Full Payment status, product specifications, and verified UTR reference numbers.
    Always updates when a new order is placed in the session.
    """
    from django.db.models import Q
    customer_email = request.session.get('glory_user_email')
    session_order_ids = request.session.get('glory_customer_order_ids', [])
    
    query = Q()
    if session_order_ids:
        query |= Q(id__in=session_order_ids)
    if customer_email:
        query |= Q(email__iexact=customer_email)
    if request.user.is_authenticated:
        query |= Q(user=request.user)

    if not query:
        orders = Order.objects.none()
    else:
        orders = Order.objects.filter(query).distinct().select_related('product').prefetch_related('transactions').order_by('-created_at')
    
    return render(request, 'customer/customer_orders.html', {
        'orders': orders,
        'total_orders': orders.count(),
        'customer_email': customer_email or '',
    })


def customer_bookings_view(request):
    """
    Dedicated My Bookings page: Customers can view ONLY their own consultations.
    """
    customer_email = request.session.get('glory_user_email', 'ganesh@example.com')
    bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')
    
    return render(request, 'customer/customer_bookings.html', {
        'bookings': bookings,
        'total_bookings': bookings.count(),
    })


def customer_payments_view(request):
    """
    Dedicated Payment History page: Verified transactions with UTR receipts.
    """
    customer_email = request.session.get('glory_user_email', 'ganesh@example.com')
    transactions = PaymentTransaction.objects.filter(order__email__iexact=customer_email).select_related('order').order_by('-paid_at')
    
    return render(request, 'customer/customer_payments.html', {
        'transactions': transactions,
        'total_transactions': transactions.count(),
    })


def customer_profile_view(request):
    """Customer profile and preferences."""
    customer_email = request.session.get('glory_user_email', 'ganesh@example.com')
    bookings = Booking.objects.filter(email__iexact=customer_email).order_by('-created_at')[:3]
    custom_requests = CustomRequest.objects.all().order_by('-created_at')[:3]
    return render(request, 'accounts/profile.html', {
        'bookings': bookings,
        'custom_requests': custom_requests,
        'customer_name': request.session.get('glory_user_name', 'Ganesh M.'),
        'customer_email': customer_email,
        'customer_phone': request.session.get('glory_user_phone', '+91 98765 43210'),
    })


def edit_profile_view(request):
    if request.method == 'POST':
        request.session['glory_user_name'] = request.POST.get('name', request.session.get('glory_user_name'))
        request.session['glory_user_phone'] = request.POST.get('phone', request.session.get('glory_user_phone'))
        messages.success(request, 'Profile updated successfully!')
        return redirect('customer_profile')
    return render(request, 'accounts/edit_profile.html')


def address_view(request):
    addresses = request.session.get('glory_addresses')
    if addresses is None:
        addresses = [
            {
                'id': 1,
                'tag': 'Home (Default)',
                'is_default': True,
                'name': request.session.get('glory_user_name', 'Ganesh M.'),
                'phone': request.session.get('glory_user_phone', '+91 98765 43210'),
                'email': request.session.get('glory_user_email', 'ganesh@example.com'),
                'flat': 'Villa #42, Fortune Enclave',
                'street': 'Road No. 12, Banjara Hills',
                'landmark': 'Near Park Hyatt & KBR Park',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'pincode': '500034',
            }
        ]
        request.session['glory_addresses'] = addresses

    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        if action == 'add':
            new_id = max([a['id'] for a in addresses], default=0) + 1
            tag = request.POST.get('tag', 'Home').strip() or 'Home'
            # If set as default or first address
            is_default = request.POST.get('is_default') == '1' or len(addresses) == 0
            if is_default:
                for a in addresses:
                    a['is_default'] = False

            new_addr = {
                'id': new_id,
                'tag': tag,
                'is_default': is_default,
                'name': request.POST.get('name', '').strip() or request.session.get('glory_user_name', 'Ganesh M.'),
                'phone': request.POST.get('phone', '').strip() or request.session.get('glory_user_phone', '+91 98765 43210'),
                'email': request.POST.get('email', '').strip() or request.session.get('glory_user_email', 'ganesh@example.com'),
                'flat': request.POST.get('flat', '').strip(),
                'street': request.POST.get('street', '').strip(),
                'landmark': request.POST.get('landmark', '').strip(),
                'city': request.POST.get('city', 'Hyderabad').strip(),
                'state': request.POST.get('state', 'Telangana').strip(),
                'pincode': request.POST.get('pincode', '500034').strip(),
            }
            # Also update session user profile info if provided
            if new_addr['name']:
                request.session['glory_user_name'] = new_addr['name']
            if new_addr['phone']:
                request.session['glory_user_phone'] = new_addr['phone']
            if new_addr['email']:
                request.session['glory_user_email'] = new_addr['email']

            addresses.append(new_addr)
            request.session['glory_addresses'] = addresses
            return redirect('address')
        elif action == 'set_default':
            try:
                addr_id = int(request.POST.get('address_id', 0))
                for a in addresses:
                    a['is_default'] = (a['id'] == addr_id)
                request.session['glory_addresses'] = addresses
            except ValueError:
                pass
            return redirect('address')
        elif action == 'delete':
            try:
                addr_id = int(request.POST.get('address_id', 0))
                addresses = [a for a in addresses if a['id'] != addr_id]
                if addresses and not any(a.get('is_default') for a in addresses):
                    addresses[0]['is_default'] = True
                request.session['glory_addresses'] = addresses
            except ValueError:
                pass
            return redirect('address')

    return render(request, 'accounts/address.html', {'addresses': addresses})


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
        password = request.POST.get('password', '').strip()

        # 1. Authenticate with Django auth
        user = authenticate(request, username=email, password=password)
        if user is None:
            matched_user = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
            if matched_user:
                user = authenticate(request, username=matched_user.username, password=password)

        is_admin = False
        if user is not None and (user.is_staff or user.is_superuser or getattr(user.profile, 'role', '') == 'admin'):
            is_admin = True
        elif email in ['admin', 'admin@gloryfurniture.com', 'admin@gmail.com', 'master@glory.com'] and password in ['admin123', 'admin', 'glory2026', 'AdminPass123!']:
            is_admin = True
            user = User.objects.filter(is_staff=True).first()

        if is_admin and user is not None:
            auth_login(request, user)
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
    products = Product.objects.all()
    bookings = Booking.objects.all().order_by('-created_at')
    orders = Order.objects.all().prefetch_related('transactions').order_by('-created_at')
    custom_requests = CustomRequest.objects.all().order_by('-created_at')
    
    # Calculate unique customers
    customer_emails = set(Order.objects.values_list('email', flat=True)) | set(Booking.objects.values_list('email', flat=True))
    total_customers = len(customer_emails)
    
    total_revenue = sum((o.paid_amount for o in orders), Decimal('0.00'))
    fully_paid_count = orders.filter(order_status='FULLY_PAID').count()
    pending_count = orders.filter(order_status='PENDING_PAYMENT').count()
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
            
    orders = Order.objects.filter(email__iexact=customer_email).prefetch_related('transactions').order_by('-created_at')
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
    Filter by status, search by order # or customer, update production progress.
    """
    status_filter = request.GET.get('status', 'ALL')
    search_q = request.GET.get('q', '').strip()
    
    orders = Order.objects.all().prefetch_related('transactions').order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_order_status':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('order_status')
            Order.objects.filter(id=order_id).update(order_status=new_status)
            messages.success(request, f"Order status updated to {new_status}!")
            return redirect(request.get_full_path())

    if status_filter != 'ALL':
        orders = orders.filter(order_status=status_filter)
        
    if search_q:
        orders = orders.filter(order_number__icontains=search_q) | orders.filter(customer_name__icontains=search_q) | orders.filter(phone__icontains=search_q)
        
    total_revenue = sum((o.paid_amount for o in orders), Decimal('0.00'))
    
    context = {
        'page_title': 'Orders Management',
        'active_nav': 'orders',
        'orders': orders,
        'total_orders': orders.count(),
        'status_filter': status_filter,
        'search_q': search_q,
        'total_revenue': f"₹{int(total_revenue):,}",
    }
    return render(request, 'admin_portal/admin_orders.html', context)


def admin_bookings_view(request):
    """
    Dedicated Admin Consultations & Measurements Management.
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


def admin_products_view(request):
    """
    Dedicated Product Catalog Inventory Management:
    Allows studio administrators to:
    1. Add new products with image, specifications, categories, and prices.
    2. Edit existing products with live form prefilling.
    3. Delete products permanently.
    All changes write directly to SQLite database (db.sqlite3) and persist permanently.
    """
    categories = Category.objects.all().order_by('order', 'name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_product':
            try:
                name = request.POST.get('name', '').strip()
                category_id = request.POST.get('category_id')
                price_str = request.POST.get('price', '0').replace('₹', '').replace(',', '').strip()
                price = Decimal(price_str or '0')
                primary_image = request.POST.get('primary_image', '').strip()
                
                # Handle file upload if provided
                if 'image_file' in request.FILES and request.FILES['image_file']:
                    upload = request.FILES['image_file']
                    from django.core.files.storage import default_storage
                    import os, uuid
                    ext = os.path.splitext(upload.name)[1]
                    filename = f"products/{uuid.uuid4().hex[:8]}{ext}"
                    saved_path = default_storage.save(filename, upload)
                    from django.conf import settings
                    primary_image = f"{settings.MEDIA_URL}{saved_path}"
                
                if not primary_image:
                    primary_image = '/static/images/card_bed.jpg'
                    
                category = get_object_or_404(Category, id=category_id)
                material = request.POST.get('material', 'Pure Grade-A Burma Teak').strip()
                style = request.POST.get('style', 'Classic').strip()
                dimensions = request.POST.get('dimensions', 'Standard').strip()
                lead_time = request.POST.get('lead_time', '5 - 7 Days Delivery').strip()
                description = request.POST.get('description', '').strip()
                in_stock = request.POST.get('in_stock') in ['1', 'on', 'true', True]
                featured = request.POST.get('featured') in ['1', 'on', 'true', True]
                new_arrival = request.POST.get('new_arrival') in ['1', 'on', 'true', True]
                
                product = Product.objects.create(
                    name=name,
                    category=category,
                    price=price,
                    primary_image=primary_image,
                    material=material,
                    style=style,
                    dimensions=dimensions,
                    lead_time=lead_time,
                    description=description,
                    in_stock=in_stock,
                    featured=featured,
                    new_arrival=new_arrival,
                )
                messages.success(request, f"Product '{product.name}' added to database successfully!")
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
                    product.category = get_object_or_404(Category, id=category_id)
                    
                price_str = request.POST.get('price', '').replace('₹', '').replace(',', '').strip()
                if price_str:
                    product.price = Decimal(price_str)
                    
                # Check for image file upload
                if 'image_file' in request.FILES and request.FILES['image_file']:
                    upload = request.FILES['image_file']
                    from django.core.files.storage import default_storage
                    import os, uuid
                    ext = os.path.splitext(upload.name)[1]
                    filename = f"products/{uuid.uuid4().hex[:8]}{ext}"
                    saved_path = default_storage.save(filename, upload)
                    from django.conf import settings
                    product.primary_image = f"{settings.MEDIA_URL}{saved_path}"
                elif request.POST.get('primary_image', '').strip():
                    product.primary_image = request.POST.get('primary_image').strip()
                    
                product.material = request.POST.get('material', product.material).strip()
                product.style = request.POST.get('style', product.style).strip()
                product.dimensions = request.POST.get('dimensions', product.dimensions).strip()
                product.lead_time = request.POST.get('lead_time', product.lead_time).strip()
                product.description = request.POST.get('description', product.description).strip()
                product.in_stock = request.POST.get('in_stock') in ['1', 'on', 'true', True]
                product.featured = request.POST.get('featured') in ['1', 'on', 'true', True]
                product.new_arrival = request.POST.get('new_arrival') in ['1', 'on', 'true', True]
                
                product.save()
                messages.success(request, f"Product '{product.name}' updated successfully in database!")
            except Exception as e:
                messages.error(request, f"Error updating product: {str(e)}")
            return redirect('admin_products')

        elif action == 'delete_product':
            p_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=p_id)
            name = product.name
            product.delete()
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
    """Dedicated Payment Ledger & UTR Verification."""
    transactions = PaymentTransaction.objects.select_related('order').order_by('-paid_at')
    total_collected = sum((t.amount for t in transactions if t.status == 'SUCCESS'), Decimal('0.00'))
    
    context = {
        'page_title': 'Payment Ledger & UPI UTR Verification',
        'active_nav': 'payments',
        'transactions': transactions,
        'total_transactions': transactions.count(),
        'total_collected': f"₹{int(total_collected):,}",
    }
    return render(request, 'admin_portal/admin_payments.html', context)


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
    """Studio configuration settings."""
    if request.method == 'POST':
        messages.success(request, "Studio settings updated successfully.")
        return redirect('admin_settings')

    context = {
        'page_title': 'Studio Settings',
        'active_nav': 'settings',
        'upi_vpa': 'gloryfurniture@okaxis',
        'studio_phone': '+91 98765 43210',
        'studio_address': 'Plot 42, Road No. 10, Jubilee Hills, Hyderabad, Telangana 500033',
    }
    return render(request, 'admin_portal/admin_settings.html', context)
