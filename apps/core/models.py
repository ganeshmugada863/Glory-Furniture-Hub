from django.db import models


class WebsiteSettings(models.Model):
    """
    Single source of truth for site-wide configuration, business identity,
    contact information, social links, and footer CMS.
    Stored permanently in the production database.
    """
    website_name = models.CharField(max_length=150, default='Glory Furniture Hub')
    tagline = models.CharField(max_length=255, default='Fine Teak Craftsmanship', blank=True)
    
    # Contact Information (Strictly empty by default - no fake or unauthorized numbers)
    primary_email = models.EmailField(max_length=254, default='support@gloryfurniture.com', blank=True)
    secondary_email = models.EmailField(max_length=254, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    whatsapp_number = models.CharField(max_length=30, blank=True, default='')
    
    # Address Details (Strictly empty by default - no fake addresses)
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    pincode = models.CharField(max_length=20, blank=True, default='')
    country = models.CharField(max_length=100, default='India', blank=True)
    
    # Footer & CMS
    footer_description = models.TextField(
        blank=True,
        default='Generations of master carpentry in Hyderabad. Specializing in seasoned solid Burma teakwood, pure mortise-and-tenon joints, and custom architectural furniture for discerning Indian homes.'
    )
    copyright_text = models.CharField(
        max_length=255,
        default='© 2026 Glory Furniture Hub. Handcrafted in Hyderabad, India.',
        blank=True
    )
    
    # Social Media URLs (Only displayed when populated)
    facebook_url = models.URLField(max_length=500, blank=True, default='')
    instagram_url = models.URLField(max_length=500, blank=True, default='')
    youtube_url = models.URLField(max_length=500, blank=True, default='')
    twitter_url = models.URLField(max_length=500, blank=True, default='')
    linkedin_url = models.URLField(max_length=500, blank=True, default='')
    
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def display_full_address(self):
        parts = [self.address, self.city, self.state, self.pincode, self.country]
        non_empty = [p.strip() for p in parts if p and p.strip() and p.strip() != 'India']
        if not non_empty:
            return ""
        if self.country and self.country.strip():
            non_empty.append(self.country.strip())
        return ", ".join(non_empty)

    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'

    def __str__(self):
        return f"{self.website_name} Settings (ID {self.id})"

    @classmethod
    def get_settings(cls):
        """Singleton accessor: returns the active WebsiteSettings instance (ID=1)."""
        settings, _ = cls.objects.get_or_create(id=1)
        return settings
