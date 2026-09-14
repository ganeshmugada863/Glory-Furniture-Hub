from django.urls import path
from . import views

urlpatterns = [
    # Customer Authentication
    path('login/', views.customer_login_view, name='login'),
    path('register/', views.customer_register_view, name='register'),
    path('accounts/google-auth/', views.google_auth_view, name='google_auth'),
    path('accounts/supabase-callback/', views.supabase_callback_view, name='supabase_callback'),
    path('logout/', views.customer_logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    
    # Customer Dedicated Portal
    path('customer/home/', views.customer_home_view, name='customer_home'),
    path('customer/dashboard/', views.customer_home_view, name='customer_dashboard'),
    path('customer/orders/', views.customer_orders_view, name='customer_orders'),
    path('customer/bookings/', views.customer_bookings_view, name='customer_bookings'),
    path('customer/payments/', views.customer_payments_view, name='customer_payments'),
    path('customer/profile/', views.customer_profile_view, name='customer_profile'),
    path('customer/profile/edit/', views.edit_profile_view, name='customer_edit_profile'),
    path('customer/address/', views.address_view, name='customer_address'),
    
    # Customer Legacy / Shortcut Routes
    path('orders/', views.customer_orders_view, name='orders'),
    path('settings/orders/', views.customer_orders_view, name='settings_orders'),
    path('profile/', views.customer_profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('address/', views.address_view, name='address'),
    path('notifications/', views.notifications_view, name='notifications'),
    
    # Admin Dedicated Authentication
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
    
    # Admin Dedicated Portal Routes
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/customers/', views.admin_customers_view, name='admin_customers'),
    path('admin/customers/<int:customer_id>/', views.admin_customer_detail_view, name='admin_customer_detail'),
    path('admin/orders/', views.admin_orders_view, name='admin_orders'),
    path('admin/bookings/', views.admin_bookings_view, name='admin_bookings'),
    path('admin/products/', views.admin_products_view, name='admin_products'),
    path('admin/categories/', views.admin_categories_view, name='admin_categories'),
    path('admin/payments/', views.admin_payments_view, name='admin_payments'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin/settings/', views.admin_settings_view, name='admin_settings'),
    
    # Admin Alias for Backward Compatibility
    path('admin-portal/', views.admin_dashboard_view, name='admin_portal'),
    path('admin/', views.admin_dashboard_view, name='admin_portal_alias'),
]
