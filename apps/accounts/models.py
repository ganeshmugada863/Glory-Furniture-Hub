from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Studio Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    full_name = models.CharField(max_length=150, default='Valued Patron', blank=True)
    phone = models.CharField(max_length=25, default='', blank=True)
    address = models.TextField(default='', blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    auth_provider = models.CharField(max_length=50, default='email')  # 'email', 'google'
    google_id = models.CharField(max_length=150, blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    cart_items = models.JSONField(default=list, blank=True)
    wishlist_ids = models.JSONField(default=list, blank=True)
    saved_addresses = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_customer(self):
        return self.role == 'customer'

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class Notification(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=50, default='general')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
