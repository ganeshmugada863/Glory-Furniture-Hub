from django.contrib import admin
from .models import UserProfile, Notification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('full_name', 'phone', 'address')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'read', 'created_at')
    list_filter = ('read', 'type')
