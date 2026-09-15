from django.urls import path
from . import views

urlpatterns = [
    # Customer Checkout & Gateway Session
    path('checkout/<str:order_number>/', views.checkout_payment_view, name='payment_checkout'),
    path('api/create-session/', views.initiate_payment_session_api, name='payment_create_session'),
    path('return/', views.payment_return_view, name='payment_return'),
    path('receipt/<str:payment_id>/', views.payment_receipt_view, name='payment_receipt'),
    path('pay-installment/<int:installment_id>/', views.pay_installment_direct_view, name='pay_installment'),

    # Cashfree Production Webhook
    path('webhook/cashfree/', views.cashfree_webhook_view, name='cashfree_webhook'),

    # Admin Payment Analytics
    path('admin-analytics/', views.admin_payments_view, name='admin_payments_analytics'),
]
