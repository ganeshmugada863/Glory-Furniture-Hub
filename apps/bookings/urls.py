from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.booking_summary_view, name='checkout'),
    path('booking/summary/', views.booking_summary_view, name='booking_summary'),
    path('booking/payment/<str:booking_id>/', views.booking_payment_view, name='booking_payment'),
    path('booking/pay-installment/<int:installment_id>/', views.pay_installment_direct_view, name='pay_installment_direct'),
    path('installment/<int:installment_id>/pay/', views.pay_installment_direct_view, name='pay_installment_direct_alias'),
    path('booking/', views.booking_view, name='booking'),
    path('booking-confirmation/<str:booking_id>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('bookings/', views.my_bookings_view, name='my_bookings'),
    path('bookings/<str:booking_id>/', views.booking_detail_view, name='booking_detail'),
    
    # Admin order detail & installment management
    path('admin-portal/order/<int:order_id>/', views.admin_order_detail_view, name='admin_order_detail'),
    path('api/orders/<int:order_id>/installments/<int:installment_id>/reschedule/', views.admin_reschedule_api, name='admin_reschedule_api'),
    
    # Secure payment webhook
    path('api/payments/webhook/', views.payment_webhook_api, name='payment_webhook'),
]

