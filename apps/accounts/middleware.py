from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse

class RoleBasedAccessMiddleware:
    """
    Middleware that enforces:
    1. The website MUST START with the Register page (/register/) for unauthenticated visitors.
    2. After registration or login:
       - Customers enter the main storefront pages (/ or /customer/home/).
       - Admins enter the Studio Admin dashboard (/admin/dashboard/).
    3. Protects /admin/* routes: Only users with role 'admin' can access them.
    4. Authenticated users visiting /login/ or /register/ are redirected to their main pages.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 0. Global forwarder from Render to Vercel
        host = request.get_host()
        if 'onrender.com' in host:
            return redirect(f"https://glory-furniture-hub.vercel.app{request.get_full_path()}", permanent=True)

        path = request.path

        # Determine user role from session and auth user
        role = request.session.get('glory_role')
        user_email = request.session.get('glory_user_email')

        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                role = 'admin'
                request.session['glory_role'] = 'admin'
            else:
                profile = getattr(request.user, 'profile', None)
                if profile and profile.role == 'admin':
                    role = 'admin'
                    request.session['glory_role'] = 'admin'
                else:
                    role = 'customer'
                    request.session['glory_role'] = 'customer'
        elif not role and user_email:
            role = 'customer'

        is_authenticated_user = bool(request.user.is_authenticated or user_email or role)
        request.user_role = role
        request.is_admin_user = (role == 'admin')
        request.is_customer_user = (role == 'customer')

        # Public auth endpoints that unauthenticated users can access
        is_auth_path = path in [
            '/register/',
            '/login/',
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/google-auth/',
            '/accounts/supabase-callback/',
            '/forgot-password/',
            '/admin/login/',
            '/admin/logout/',
        ]
        is_static_or_api = (
            path.startswith('/static/') or
            path.startswith('/media/') or
            path.startswith('/api/') or
            path in ['/favicon.ico', '/favicon.svg', '/robots.txt', '/sitemap.xml']
        )

        is_payment_path = (
            path.startswith('/payments/') or
            path.startswith('/installment/') or
            path.startswith('/booking/payment/') or
            path.startswith('/booking-confirmation/')
        )

        # Public storefront pages that visitors can freely browse
        is_public_storefront = (
            path in ['/', '/home/', '/home', '/welcome/', '/welcome', '/store/', '/store'] or
            path.startswith('/catalog') or
            path.startswith('/collection') or
            path.startswith('/shop') or
            path.startswith('/product/') or
            path.startswith('/search') or
            path in ['/about/', '/contact/', '/faq/', '/guide/', '/splash/', '/onboarding/']
        )

        # 1. ADMIN ROUTE GUARD
        is_admin_path = (path.startswith('/admin/') or path.startswith('/admin-portal')) and not path.startswith('/django-admin/')
        is_admin_auth_path = path in ['/admin/login/', '/admin/logout/']

        if is_admin_path and not is_admin_auth_path:
            is_valid_admin = (
                request.user.is_authenticated and (
                    request.user.is_staff or 
                    request.user.is_superuser or 
                    getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
                )
            )
            if not is_valid_admin:
                if path.startswith('/admin-portal'):
                    return HttpResponseForbidden("Access Denied: Admin privileges required.")
                if request.user.is_authenticated:
                    messages.error(request, 'Access Denied: Admin privileges required.')
                    return redirect('home')
                else:
                    return redirect(f'/admin/login/?next={path}')

        # If admin visits /admin/login/ while already logged in, redirect to admin dashboard
        if path == '/admin/login/' and role == 'admin':
            return redirect('admin_dashboard')

        # 2. PROTECTED CUSTOMER ROUTES (Cart, Checkout, Booking, Profile) REQUIRE ACCOUNT
        if not is_authenticated_user and not is_auth_path and not is_static_or_api and not is_public_storefront and not is_payment_path:
            return redirect(f'/register/?next={path}')

        # 3. IF AUTHENTICATED USER VISITS REGISTER/LOGIN, REDIRECT TO HOME (UNLESS EXPLICIT NEXT)
        if is_authenticated_user and path in ['/login/', '/register/']:
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')

        response = self.get_response(request)
        return response

