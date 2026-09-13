from django.shortcuts import redirect
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
        path = request.path

        # Determine user role from session and auth user
        role = request.session.get('glory_role')
        user_email = request.session.get('glory_user_email')

        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                role = 'admin'
                request.session['glory_role'] = 'admin'
            elif not role:
                role = 'customer'
                request.session['glory_role'] = role
        elif not role and user_email:
            if user_email in ['admin', 'admin@gloryfurniture.com', 'admin@gmail.com', 'master@glory.com']:
                role = 'admin'
                request.session['glory_role'] = 'admin'

        is_authenticated_user = bool(request.user.is_authenticated or user_email or role)
        request.user_role = role
        request.is_admin_user = (role == 'admin')
        request.is_customer_user = (role == 'customer')

        # Public auth endpoints that unauthenticated users can access
        is_auth_path = path in [
            '/register/',
            '/login/',
            '/accounts/google-auth/',
            '/forgot-password/',
            '/admin/login/',
            '/admin/logout/',
        ]
        is_static_or_api = (
            path.startswith('/static/') or
            path.startswith('/media/') or
            path.startswith('/api/') or
            path == '/favicon.ico' or
            path == '/favicon.svg'
        )

        # 1. ADMIN ROUTE GUARD
        is_admin_path = (path.startswith('/admin/') and not path.startswith('/django-admin/')) or path.startswith('/admin-portal')
        is_admin_auth_path = path in ['/admin/login/', '/admin/logout/', '/admin-portal/login/']

        if is_admin_path and not is_admin_auth_path:
            if role != 'admin':
                if role == 'customer':
                    messages.error(request, 'Access Denied: Admin privileges required.')
                    return redirect('home')
                else:
                    return redirect(f'/admin/login/?next={path}')

        # If admin visits /admin/login/ while already logged in, redirect to admin dashboard
        if path == '/admin/login/' and role == 'admin':
            return redirect('admin_dashboard')

        # 2. THE WEBSITE MUST START WITH REGISTER PAGE FOR ALL UNAUTHENTICATED VISITORS
        if not is_authenticated_user and not is_auth_path and not is_static_or_api:
            return redirect('register')

        # 3. IF AUTHENTICATED USER VISITS REGISTER/LOGIN, REDIRECT TO MAIN PAGES
        if path in ['/login/', '/register/']:
            if role == 'admin':
                return redirect('admin_dashboard')
            elif is_authenticated_user:
                return redirect('home')

        # 4. IF ADMIN VISITS MAIN STOREFRONT ROOT, REDIRECT TO ADMIN CONSOLE
        if path == '/' and role == 'admin':
            return redirect('admin_dashboard')

        response = self.get_response(request)
        return response

