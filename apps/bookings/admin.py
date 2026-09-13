from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'consultation_type', 'preferred_date', 'time_slot', 'status', 'created_at')
    list_filter = ('status', 'consultation_type', 'preferred_date')
    search_fields = ('booking_id', 'customer_name', 'email', 'phone')
