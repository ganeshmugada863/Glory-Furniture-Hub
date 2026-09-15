from django.contrib import admin
from .models import InstallmentPlan, Payment, WebhookEvent

@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'installment_count', 'interval_days', 'min_amount', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'payment_type', 'amount', 'gateway', 'gateway_payment_id', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'payment_type', 'gateway')
    search_fields = ('payment_id', 'gateway_order_id', 'gateway_payment_id', 'order__order_number', 'order__customer_name', 'order__email')
    readonly_fields = ('payment_id', 'created_at', 'updated_at', 'paid_at')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_type', 'gateway_order_id', 'status', 'received_at', 'processed_at')
    list_filter = ('status', 'event_type')
    search_fields = ('event_id', 'gateway_order_id', 'gateway_payment_id', 'payload_hash')
    readonly_fields = ('received_at', 'processed_at')
