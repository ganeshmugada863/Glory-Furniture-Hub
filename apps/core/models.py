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


class PageCMSContent(models.Model):
    """
    Dedicated CMS model for Welcome, Login, and Register pages.
    Allows administrators to customize all headlines, descriptions, badges,
    and hero images dynamically from the Admin Portal.
    """
    # === WELCOME PAGE CMS ===
    welcome_bg_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    welcome_bg_image_url = models.URLField(max_length=1000, blank=True, default='')
    welcome_eyebrow = models.CharField(max_length=200, default='WELCOME TO')
    welcome_title_main = models.CharField(max_length=200, default='Glory')
    welcome_title_highlight = models.CharField(max_length=200, default='Furniture Hub')
    welcome_cta_text = models.CharField(max_length=100, default='Get Started')
    welcome_badge1_title = models.CharField(max_length=100, default='Modern Designs')
    welcome_badge2_title = models.CharField(max_length=100, default='Trusted Quality')
    welcome_badge3_title = models.CharField(max_length=100, default='Safe Delivery')

    # === LOGIN PAGE CMS ===
    login_slide1_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    login_slide1_image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        default='https://lh3.googleusercontent.com/aida/AEtjO1W7s1H6HLs_yNUpBwueaww35O5laxZ5AP0g7J4UDx4PHugVL5djKq-6BULWAG0WACZVA_huQ30HTSZINIOYoXeUwv-vTvFI-OULSFOFIBxSqjHg01I_ZmMfUGn0M8Og8BEvvW1yl0FzNDCUAiXmGcMILvDIbiZG10Nroh1KxEUNmS7Z71xLaDx9Fy37E0NjS7-bcT7FwY2CKrYaGrzISS6LpZ1QsJdvaE2TjT0XuE0Pu-74fdaNCZDKzhg'
    )
    login_slide2_image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        default='https://lh3.googleusercontent.com/aida/AEtjO1Uxw6WL1UygfI-XYJNyq47ksbYE4c4u6ptdffKKojNqw14sDVM1BszDEAC6Dr98oRXU4BngcLjDilAn9HU6OKg0wNQfrtDjEcBi8EJ_BHRWtw2SAtqmKb_OJQO2pqzYFflUFSsAPxzSba74X5Sm0C1_saragShT6aPlFbymQTSOp308wUoPfkiFYh3Y-WgpOgYq7jrZsNvfBVU8i2Gp9_WOs6Vdc_HBYXpmCKX-JalLdyOUi-2ibdLdlAg'
    )
    login_slide3_image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        default='https://lh3.googleusercontent.com/aida/AEtjO1XQpLWAVX5fET2usaL2iEHeOkAwyq287h2Obq9elLp8XTDq7E86i8apiUE1xd5fLRiHX2u_uaAuodl1WZVOKfdHxt8DdbIY0OSszt664oT5I2gfvapwMT0NhvzyiygqhuxnVXSxTzOfLil2R24wbSA4vB7SGpTsBHfsYhrevVGC4Sih2ZFSmja83k5LfnA7W4GWTinFgkDZZpVwT1XOxnBVb21uH5fXBWVONvqhw7OJbyXZ8HyDdL6N3v8'
    )
    login_hero_title = models.CharField(max_length=200, default='Welcome Back')
    login_hero_highlight = models.CharField(max_length=200, default='Glory Furniture Hub')
    login_card_subtitle = models.CharField(max_length=200, default='CLIENT AUTHENTICATION')
    login_card_title = models.CharField(max_length=200, default='Welcome Back')
    login_card_description = models.TextField(default='Sign in to track orders, consultation bookings, and saved blueprints')
    login_badge1_title = models.CharField(max_length=150, default='Order Tracking')
    login_badge1_desc = models.CharField(max_length=255, default='Live kiln, joinery & white-glove transport tracking.')
    login_badge2_title = models.CharField(max_length=150, default='Blueprint Vault')
    login_badge2_desc = models.CharField(max_length=255, default='Architect CAD specifications and custom timber grains.')
    login_badge3_title = models.CharField(max_length=150, default='Collector Privileges')
    login_badge3_desc = models.CharField(max_length=255, default='Reserved kiln batches & master woodworker sessions.')

    # === REGISTER PAGE CMS ===
    register_slide1_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    register_slide1_image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        default='https://lh3.googleusercontent.com/aida/AEtjO1W7s1H6HLs_yNUpBwueaww35O5laxZ5AP0g7J4UDx4PHugVL5djKq-6BULWAG0WACZVA_huQ30HTSZINIOYoXeUwv-vTvFI-OULSFOFIBxSqjHg01I_ZmMfUGn0M8Og8BEvvW1yl0FzNDCUAiXmGcMILvDIbiZG10Nroh1KxEUNmS7Z71xLaDx9Fy37E0NjS7-bcT7FwY2CKrYaGrzISS6LpZ1QsJdvaE2TjT0XuE0Pu-74fdaNCZDKzhg'
    )
    register_slide2_image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        default='https://lh3.googleusercontent.com/aida/AEtjO1Uxw6WL1UygfI-XYJNyq47ksbYE4c4u6ptdffKKojNqw14sDVM1BszDEAC6Dr98oRXU4BngcLjDilAn9HU6OKg0wNQfrtDjEcBi8EJ_BHRWtw2SAtqmKb_OJQO2pqzYFflUFSsAPxzSba74X5Sm0C1_saragShT6aPlFbymQTSOp308wUoPfkiFYh3Y-WgpOgYq7jrZsNvfBVU8i2Gp9_WOs6Vdc_HBYXpmCKX-JalLdyOUi-2ibdLdlAg'
    )
    register_slide3_image_url = models.URLField(
        max_length=1000, 
        blank=True, 
        default='https://lh3.googleusercontent.com/aida/AEtjO1XQpLWAVX5fET2usaL2iEHeOkAwyq287h2Obq9elLp8XTDq7E86i8apiUE1xd5fLRiHX2u_uaAuodl1WZVOKfdHxt8DdbIY0OSszt664oT5I2gfvapwMT0NhvzyiygqhuxnVXSxTzOfLil2R24wbSA4vB7SGpTsBHfsYhrevVGC4Sih2ZFSmja83k5LfnA7W4GWTinFgkDZZpVwT1XOxnBVb21uH5fXBWVONvqhw7OJbyXZ8HyDdL6N3v8'
    )
    register_hero_badge = models.CharField(max_length=200, default='BURMA TEAK MINIMALIST BED')
    register_hero_title = models.CharField(max_length=200, default='Glory Furniture Hub')
    register_hero_desc = models.TextField(default='Experience timeless Burma teak mastery shaped with precision joinery and sustainable heritage craft')
    register_card_subtitle = models.CharField(max_length=200, default='HAND-CRAFTED SOLID BURMA TEAK')
    register_card_title = models.CharField(max_length=200, default='Create Customer Account')
    register_card_description = models.TextField(default='Access exclusive handcrafted solid teak collections & custom orders')
    register_badge1_title = models.CharField(max_length=150, default='Sign up account')
    register_badge1_desc = models.CharField(max_length=255, default='Basic credentials & authentication.')
    register_badge2_title = models.CharField(max_length=150, default='Bespoke preferences')
    register_badge2_desc = models.CharField(max_length=255, default='Wood grains, finish & dimensions.')
    register_badge3_title = models.CharField(max_length=150, default='VIP catalog access')
    register_badge3_desc = models.CharField(max_length=255, default='Private studio consults & pricing.')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Page CMS Content'
        verbose_name_plural = 'Page CMS Content'

    def __str__(self):
        return f"Auth & Welcome CMS Content (ID {self.id})"

    @classmethod
    def get_cms(cls):
        """Singleton accessor: returns the active PageCMSContent instance (ID=1)."""
        cms, _ = cls.objects.get_or_create(id=1)
        return cms

    @property
    def welcome_image(self):
        if self.welcome_bg_image:
            return self.welcome_bg_image.url
        if self.welcome_bg_image_url:
            return self.welcome_bg_image_url
        return '/static/images/welcome_bg_stitch.jpg'

    @property
    def login_image1(self):
        if self.login_slide1_image:
            return self.login_slide1_image.url
        return self.login_slide1_image_url

    @property
    def register_image1(self):
        if self.register_slide1_image:
            return self.register_slide1_image.url
        return self.register_slide1_image_url

