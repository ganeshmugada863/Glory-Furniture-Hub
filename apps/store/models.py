from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    room_type = models.CharField(max_length=120, blank=True, default='')
    image = models.CharField(max_length=500, blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    STYLE_CHOICES = [
        ('Classic', 'Classic'),
        ('Modern Minimalist', 'Modern Minimalist'),
        ('Rustic', 'Rustic'),
        ('Traditional', 'Traditional'),
    ]

    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=1)
    material = models.CharField(max_length=250, default='Solid Teak Wood')
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='Classic')
    dimensions = models.CharField(max_length=250, default='Standard')
    lead_time = models.CharField(max_length=120, default='5 - 7 Days Delivery')
    description = models.TextField(blank=True)
    
    # Store JSON lists for finishes, size variants, secondary images
    finishes = models.JSONField(default=list, blank=True)
    size_variants = models.JSONField(default=list, blank=True)
    
    primary_image = models.CharField(max_length=500, default='')
    secondary_images = models.JSONField(default=list, blank=True)
    
    featured = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            import uuid
            base_slug = slugify(self.name, allow_unicode=True)
            if not base_slug or not base_slug.strip():
                base_slug = f"product-{uuid.uuid4().hex[:6]}"
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def all_images(self):
        images = []
        if self.primary_image and self.primary_image.strip():
            images.append(self.primary_image.strip())
        if self.secondary_images and isinstance(self.secondary_images, list):
            for img in self.secondary_images:
                if img and isinstance(img, str) and img.strip() and img.strip() not in images:
                    images.append(img.strip())
        return images or ['/static/images/card_bed.jpg']

    @property
    def formatted_price(self):
        """Format price in Indian Rupee format, e.g., ₹99,999"""
        val = int(self.price)
        s = str(val)
        if len(s) <= 3:
            return f"₹{s}"
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        return f"₹{','.join(groups)},{last3}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.product.name} ({self.rating}★)"
