from django.contrib import admin
from .models import Booking, Order, OrderStatusHistory, OrderAdminAuditLog

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'consultation_type', 'preferred_date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'consultation_type', 'preferred_date')
    search_fields = ('booking_id', 'customer_name', 'email', 'phone')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'product_name', 'total_amount', 'paid_amount', 'remaining_amount', 'payment_status', 'fulfillment_status', 'created_at')
    list_editable = ('fulfillment_status',)
    list_filter = ('fulfillment_status', 'payment_status', 'payment_plan')
    search_fields = ('order_number', 'customer_name', 'email', 'phone')

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'previous_status', 'fulfillment_status', 'changed_by', 'admin_notes', 'created_at')
    list_filter = ('fulfillment_status', 'created_at')
    search_fields = ('order__order_number', 'admin_notes')

@admin.register(OrderAdminAuditLog)
class OrderAdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'action', 'performed_by', 'old_value', 'new_value', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('order__order_number', 'notes')
