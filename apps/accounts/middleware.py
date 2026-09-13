from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class RoleBasedAccessMiddleware:
    """
    Middleware that strictly enforces separation between Customer and Admin portals.
    1. Protects /admin/* routes: Only users with role 'admin' can access them.
       - Unauthorized customers are redirected to /customer/home/.
       - Unauthenticated users are redirected to /admin/login/.
    2. Protects /customer/* routes: Only users with role 'customer' can access them.
       - Admin users attempting to access customer pages are redirected to /admin/dashboard/.
       - Unauthenticated users are redirected to /login/.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Determine user role from session and auth user
        role = request.session.get('glory_role')
        if not role:
            if request.user.is_authenticated:
                if request.user.is_staff or request.user.is_superuser:
                    role = 'admin'
                else:
                    role = 'customer'
                request.session['glory_role'] = role

        request.user_role = role
        request.is_admin_user = (role == 'admin')
        request.is_customer_user = (role == 'customer')

        # 1. ADMIN ROUTE GUARD
        # Protect all /admin/* routes except /admin/login/ and /admin/logout/ and /django-admin/
        is_admin_path = (path.startswith('/admin/') and not path.startswith('/django-admin/')) or path.startswith('/admin-portal')
        is_admin_auth_path = path in ['/admin/login/', '/admin/logout/', '/admin-portal/login/']

        if is_admin_path and not is_admin_auth_path:
            if role != 'admin':
                if role == 'customer':
                    # Customer attempting to access admin route -> Deny and redirect to customer home
                    messages.error(request, 'Access Denied: Admin privileges required.')
                    return redirect('customer_home')
                else:
                    # Unauthenticated -> redirect to dedicated admin login
                    return redirect(f'/admin/login/?next={path}')

        # If admin visits /admin/login/ while already logged in, redirect to admin dashboard
        if path == '/admin/login/' and role == 'admin':
            return redirect('admin_dashboard')

        # 2. CUSTOMER PORTAL ROUTES
        # Customer portal routes and orders are open to all customers and patrons.
        # NEVER redirect customer orders to admin dashboard!
        if path in ['/login/', '/register/'] and role == 'customer':
            return redirect('customer_home')

        response = self.get_response(request)
        return response
