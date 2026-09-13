from django.contrib import admin
from .models import CustomRequest

@admin.register(CustomRequest)
class CustomRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'customer_name', 'category', 'wood_type', 'budget_range', 'status', 'created_at')
    list_filter = ('status', 'wood_type')
    search_fields = ('request_id', 'customer_name', 'email', 'phone', 'category')
