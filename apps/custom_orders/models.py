from django.db import models
import uuid

class CustomRequest(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Estimation In Progress', 'Estimation In Progress'),
        ('Quote Sent', 'Quote Sent'),
        ('Approved', 'Approved'),
        ('Crafting Started', 'Crafting Started'),
        ('Delivered', 'Delivered'),
    ]

    request_id = models.CharField(max_length=50, unique=True, blank=True)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    category = models.CharField(max_length=120, default='Custom Living / Dining Piece')
    wood_type = models.CharField(max_length=120, default='Pure Grade-A Burma Teak')
    dimensions = models.CharField(max_length=200, blank=True, default='')
    budget_range = models.CharField(max_length=100, default='₹50,000 - ₹1,00,000')
    description = models.TextField(blank=True, default='')
    reference_image = models.CharField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Submitted')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = f"GLORY-REQ-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_id} - {self.customer_name} ({self.category})"
