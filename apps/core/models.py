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
        try:
            cms, _ = cls.objects.get_or_create(id=1)
            return cms
        except Exception:
            return cls(id=1)

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


class HomeMediaCMS(models.Model):
    """
    Dedicated CMS model for the Home Hero Showcase Cards, Categories, and Video Banners.
    Allows administrators to upload or update images and video URLs directly from the Admin Portal.
    """
    # 4 Hero Cards
    hero_card_1_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    hero_card_1_url = models.TextField(blank=True, default='/static/images/hero_card_living_clean.jpg')
    hero_card_1_title = models.CharField(max_length=200, default='The Living Edit')
    hero_card_1_subtitle = models.CharField(max_length=255, default='Warm, timeless essentials')

    hero_card_2_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    hero_card_2_url = models.TextField(blank=True, default='/static/images/hero_card_bed_full.jpg')
    hero_card_2_title = models.CharField(max_length=200, default='Soft Retreats')
    hero_card_2_subtitle = models.CharField(max_length=255, default='Rest in natural comfort')

    hero_card_3_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    hero_card_3_url = models.TextField(blank=True, default='/static/images/hero_card_dining_full.jpg')
    hero_card_3_title = models.CharField(max_length=200, default='Gather & Dine')
    hero_card_3_subtitle = models.CharField(max_length=255, default='Spaces for meaningful moments')

    hero_card_4_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    hero_card_4_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuBP6Sc2G1ga1CiPRkIPjlFaE4nLFkuJKMJufcJ3XraTvuqM70_TjdbaX8DqUYVLYrbmH0bdrorwT6ULYwBOMmsfEuxDN2bqvx5wd72KCTjWKKh1XJSFqLVOMTEvNJTGmwuYIHMqrRYmHhpV6dBbP5hVhEVg9PPIyzvgYJb-RBcwvZb1ZR7xelUEL26wh_OZzoxcaYT7s5lRoW5rq5sMFtjDaUehA94PJRn4LO8MVcFANFFBp_JrB-w')
    hero_card_4_title = models.CharField(max_length=200, default='Artisan Sanctuaries')
    hero_card_4_subtitle = models.CharField(max_length=255, default='Bespoke handcrafted suites')

    hero_card_5_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    hero_card_5_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuBfiW_WTyRCjiNePezPop4j9QGCOkz68YNMPRhRu1fMVWzgItVDsALH4pRnidHUjQgywuEHvNR8ze_1VGBrZrA3rn8ARj47fI5p6uVLmiWaOC6WIU9O-eqdVmb5EfJ2N7YH6WYOYm-el7G28elk70IzRIM26cpbpSVFSzPwblOUOCTKTUlGPVdNBGoXKrKvEcWbnVxIWL9d84y9tEiCdCNhBVHNvjAGIpMkBr6ckwIp_m-vvLIMAmA')
    hero_card_5_title = models.CharField(max_length=200, default='Nordic Bouclé Living')
    hero_card_5_subtitle = models.CharField(max_length=255, default='Sculptural lounge aesthetic')

    hero_card_6_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    hero_card_6_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuAeX-7-m4xsZYUC1QI8Uul1nEoQ3G4b-o0GbQrVoGzRA1X56EcWlz-F5_KbtccY4AOAzW6RtFfqG-7VBfxqbnvfLXgiIgtKWgzDzBpa3Ix503c-nFY2APbz9Dkr-xxRAR_Sy4NwKzkvBr0-aUe4_bIOw3EALXmwSX7VmYGOzm8fX5_uF-WUF0Ame1zwakgBIZBlUOzuqpz3abxrpBxnffu2t4knM5FSJqDqUCUfjCrBCaDHT5hqUEM')
    hero_card_6_title = models.CharField(max_length=200, default='Architectural Pavilion')
    hero_card_6_subtitle = models.CharField(max_length=255, default='Generational teak mastery')

    # 8 Category Circles
    cat_beds_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_beds_url = models.TextField(blank=True, default='/static/images/cat_beds.png')

    cat_sofa_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_sofa_url = models.TextField(blank=True, default='/static/images/cat_sofa.png')

    cat_diwan_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_diwan_url = models.TextField(blank=True, default='/static/images/cat_diwan.png')

    cat_dining_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_dining_url = models.TextField(blank=True, default='/static/images/cat_dining.png')

    cat_dressing_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_dressing_url = models.TextField(blank=True, default='/static/images/cat_dressing.png')

    cat_doors_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_doors_url = models.TextField(blank=True, default='/static/images/cat_doors.png')

    cat_teapoy_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_teapoy_url = models.TextField(blank=True, default='/static/images/cat_teapoy.png')

    cat_podiums_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    cat_podiums_url = models.TextField(blank=True, default='/static/images/cat_podiums.png')

    # Craft / Atelier Showcase Banner
    craft_banner_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    craft_banner_url = models.TextField(blank=True, default='')
    craft_banner_title = models.CharField(max_length=200, default='The Living Space & Atelier', blank=True)
    craft_banner_subtitle = models.CharField(max_length=255, default='Handcrafted architectural sanctuaries', blank=True)

    # Second Carousel: 3D Coverflow Showcase ("Immersive Spaces & Showcases" - 5 Cards)
    coverflow_card_1_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    coverflow_card_1_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuBfiW_WTyRCjiNePezPop4j9QGCOkz68YNMPRhRu1fMVWzgItVDsALH4pRnidHUjQgywuEHvNR8ze_1VGBrZrA3rn8ARj47fI5p6uVLmiWaOC6WIU9O-eqdVmb5EfJ2N7YH6WYOYm-el7G28elk70IzRIM26cpbpSVFSzPwblOUOCTKTUlGPVdNBGoXKrKvEcWbnVxIWL9d84y9tEiCdCNhBVHNvjAGIpMkBr6ckwIp_m-vvLIMAmA')
    coverflow_card_1_title = models.CharField(max_length=200, default='The Nordic Bouclé Living Suite')
    coverflow_card_1_tag = models.CharField(max_length=100, default='Living Room Concept')

    coverflow_card_2_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    coverflow_card_2_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuCNPj-zu7tcX6-s8dGzgXSL1uMOkEDNA2AwG9ID-NEX-GKmqi2oaVuN6NKut8NAgm1jCG815bCJkw2DaSdQc2A8pwV-YV1fXakGxuxYJ2fPAw6C33SSpYh2kg__h_lzOhVcFtEZM4ZkW3qBGehNHsspih6lTcN9bbQj5oVZpFvOUwJJHDabdHDBN-DCf-EqoFDrxCJwh6EdiiA6JRJfXTpNysOAjYnksA8BZaFyOyIY7euJH7_FWcc')
    coverflow_card_2_title = models.CharField(max_length=200, default='Solid Teak Master Sanctuary')
    coverflow_card_2_tag = models.CharField(max_length=100, default='Master Bedroom')

    coverflow_card_3_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    coverflow_card_3_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuCpWLaMHEgbC4_C1cno63yFYn-ZAiwq8fhl_WCgfjafYjSBRmnsvWc8XXTN5QNSqiPtxF7VAdcBKVyNRN8D44uF-XYX1CSN1pZSBPXuh5c8oUx2ijEbNIZsE2r5Zi2Rx70rL6pEeykovA6XKXsR9384MuJJkSHITcWe9-YQU4C9Ptr6384CaR1zkWzPsa1Mw-RkjfFuB4jN7dmo-7OiTf7C_LJBBawCwqaruN5scXLPhLkONk_ZGpQ')
    coverflow_card_3_title = models.CharField(max_length=200, default='Artisan Teak & Oak Dining Hall')
    coverflow_card_3_tag = models.CharField(max_length=100, default='Dining & Entertaining')

    coverflow_card_4_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    coverflow_card_4_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuBP6Sc2G1ga1CiPRkIPjlFaE4nLFkuJKMJufcJ3XraTvuqM70_TjdbaX8DqUYVLYrbmH0bdrorwT6ULYwBOMmsfEuxDN2bqvx5wd72KCTjWKKh1XJSFqLVOMTEvNJTGmwuYIHMqrRYmHhpV6dBbP5hVhEVg9PPIyzvgYJb-RBcwvZb1ZR7xelUEL26wh_OZzoxcaYT7s5lRoW5rq5sMFtjDaUehA94PJRn4LO8MVcFANFFBp_JrB-w')
    coverflow_card_4_title = models.CharField(max_length=200, default='Sculptural Reading & Diwan Nook')
    coverflow_card_4_tag = models.CharField(max_length=100, default='Atelier Sanctuary')

    coverflow_card_5_image = models.ImageField(upload_to='cms/', blank=True, null=True)
    coverflow_card_5_url = models.TextField(blank=True, default='https://lh3.googleusercontent.com/aida-public/AB6AXuAeX-7-m4xsZYUC1QI8Uul1nEoQ3G4b-o0GbQrVoGzRA1X56EcWlz-F5_KbtccY4AOAzW6RtFfqG-7VBfxqbnvfLXgiIgtKWgzDzBpa3Ix503c-nFY2APbz9Dkr-xxRAR_Sy4NwKzkvBr0-aUe4_bIOw3EALXmwSX7VmYGOzm8fX5_uF-WUF0Ame1zwakgBIZBlUOzuqpz3abxrpBxnffu2t4knM5FSJqDqUCUfjCrBCaDHT5hqUEM')
    coverflow_card_5_title = models.CharField(max_length=200, default='Bespoke Architectural Pavilion')
    coverflow_card_5_tag = models.CharField(max_length=100, default='Hospitality & Suite')

    # Showcase Video Banner
    video_showcase_file = models.FileField(upload_to='cms/videos/', blank=True, null=True)
    video_showcase_url = models.TextField(blank=True, default='/static/videos/product_1.mp4')
    video_tagline = models.CharField(max_length=200, default='Glory Atelier • Archival Series')
    video_title = models.CharField(max_length=255, default='Chapter 04: Handcrafted Royal Teak Bedroom Collection')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Home Media CMS'
        verbose_name_plural = 'Home Media CMS'

    def __str__(self):
        return f"Home Media CMS (ID {self.id})"

    @classmethod
    def get_cms(cls):
        try:
            cms, _ = cls.objects.get_or_create(id=1)
            return cms
        except Exception:
            return cls(id=1)

    # Helper properties returning active image or URL
    @property
    def hero_1(self):
        if self.hero_card_1_url and self.hero_card_1_url.strip():
            return self.hero_card_1_url.strip()
        if self.hero_card_1_image:
            try:
                return self.hero_card_1_image.url
            except Exception:
                pass
        return '/static/images/hero_card_living_clean.jpg'

    @property
    def hero_2(self):
        if self.hero_card_2_url and self.hero_card_2_url.strip():
            return self.hero_card_2_url.strip()
        if self.hero_card_2_image:
            try:
                return self.hero_card_2_image.url
            except Exception:
                pass
        return '/static/images/hero_card_bed_full.jpg'

    @property
    def hero_3(self):
        if self.hero_card_3_url and self.hero_card_3_url.strip():
            return self.hero_card_3_url.strip()
        if self.hero_card_3_image:
            try:
                return self.hero_card_3_image.url
            except Exception:
                pass
        return '/static/images/hero_card_dining_full.jpg'

    @property
    def hero_4(self):
        if self.hero_card_4_url and self.hero_card_4_url.strip():
            return self.hero_card_4_url.strip()
        if self.hero_card_4_image:
            try:
                return self.hero_card_4_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuBP6Sc2G1ga1CiPRkIPjlFaE4nLFkuJKMJufcJ3XraTvuqM70_TjdbaX8DqUYVLYrbmH0bdrorwT6ULYwBOMmsfEuxDN2bqvx5wd72KCTjWKKh1XJSFqLVOMTEvNJTGmwuYIHMqrRYmHhpV6dBbP5hVhEVg9PPIyzvgYJb-RBcwvZb1ZR7xelUEL26wh_OZzoxcaYT7s5lRoW5rq5sMFtjDaUehA94PJRn4LO8MVcFANFFBp_JrB-w'

    @property
    def hero_5(self):
        if self.hero_card_5_url and self.hero_card_5_url.strip():
            return self.hero_card_5_url.strip()
        if self.hero_card_5_image:
            try:
                return self.hero_card_5_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuBfiW_WTyRCjiNePezPop4j9QGCOkz68YNMPRhRu1fMVWzgItVDsALH4pRnidHUjQgywuEHvNR8ze_1VGBrZrA3rn8ARj47fI5p6uVLmiWaOC6WIU9O-eqdVmb5EfJ2N7YH6WYOYm-el7G28elk70IzRIM26cpbpSVFSzPwblOUOCTKTUlGPVdNBGoXKrKvEcWbnVxIWL9d84y9tEiCdCNhBVHNvjAGIpMkBr6ckwIp_m-vvLIMAmA'

    @property
    def hero_6(self):
        if self.hero_card_6_url and self.hero_card_6_url.strip():
            return self.hero_card_6_url.strip()
        if self.hero_card_6_image:
            try:
                return self.hero_card_6_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuAeX-7-m4xsZYUC1QI8Uul1nEoQ3G4b-o0GbQrVoGzRA1X56EcWlz-F5_KbtccY4AOAzW6RtFfqG-7VBfxqbnvfLXgiIgtKWgzDzBpa3Ix503c-nFY2APbz9Dkr-xxRAR_Sy4NwKzkvBr0-aUe4_bIOw3EALXmwSX7VmYGOzm8fX5_uF-WUF0Ame1zwakgBIZBlUOzuqpz3abxrpBxnffu2t4knM5FSJqDqUCUfjCrBCaDHT5hqUEM'

    @property
    def cat_beds(self):
        if self.cat_beds_url and self.cat_beds_url.strip():
            return self.cat_beds_url.strip()
        if self.cat_beds_image:
            try:
                return self.cat_beds_image.url
            except Exception:
                pass
        return '/static/images/cat_beds.png'

    @property
    def cat_sofa(self):
        if self.cat_sofa_url and self.cat_sofa_url.strip():
            return self.cat_sofa_url.strip()
        if self.cat_sofa_image:
            try:
                return self.cat_sofa_image.url
            except Exception:
                pass
        return '/static/images/cat_sofa.png'

    @property
    def cat_diwan(self):
        if self.cat_diwan_url and self.cat_diwan_url.strip():
            return self.cat_diwan_url.strip()
        if self.cat_diwan_image:
            try:
                return self.cat_diwan_image.url
            except Exception:
                pass
        return '/static/images/cat_diwan.png'

    @property
    def cat_dining(self):
        if self.cat_dining_url and self.cat_dining_url.strip():
            return self.cat_dining_url.strip()
        if self.cat_dining_image:
            try:
                return self.cat_dining_image.url
            except Exception:
                pass
        return '/static/images/cat_dining.png'

    @property
    def cat_dressing(self):
        if self.cat_dressing_url and self.cat_dressing_url.strip():
            return self.cat_dressing_url.strip()
        if self.cat_dressing_image:
            try:
                return self.cat_dressing_image.url
            except Exception:
                pass
        return '/static/images/cat_dressing.png'

    @property
    def cat_doors(self):
        if self.cat_doors_url and self.cat_doors_url.strip():
            return self.cat_doors_url.strip()
        if self.cat_doors_image:
            try:
                return self.cat_doors_image.url
            except Exception:
                pass
        return '/static/images/cat_doors.png'

    @property
    def cat_teapoy(self):
        if self.cat_teapoy_url and self.cat_teapoy_url.strip():
            return self.cat_teapoy_url.strip()
        if self.cat_teapoy_image:
            try:
                return self.cat_teapoy_image.url
            except Exception:
                pass
        return '/static/images/cat_teapoy.png'

    @property
    def cat_podiums(self):
        if self.cat_podiums_url and self.cat_podiums_url.strip():
            return self.cat_podiums_url.strip()
        if self.cat_podiums_image:
            try:
                return self.cat_podiums_image.url
            except Exception:
                pass
        return '/static/images/cat_podiums.png'

    @property
    def video_url(self):
        if self.video_showcase_url and self.video_showcase_url.strip():
            return self.video_showcase_url.strip()
        if self.video_showcase_file:
            try:
                return self.video_showcase_file.url
            except Exception:
                pass
        return '/static/videos/product_1.mp4'

    @property
    def craft_banner(self):
        if self.craft_banner_url and self.craft_banner_url.strip():
            return self.craft_banner_url.strip()
        if self.craft_banner_image:
            try:
                return self.craft_banner_image.url
            except Exception:
                pass
        return '/static/images/hero_card_living_clean.jpg'

    @property
    def coverflow_1(self):
        if self.coverflow_card_1_url and self.coverflow_card_1_url.strip():
            return self.coverflow_card_1_url.strip()
        if self.coverflow_card_1_image:
            try:
                return self.coverflow_card_1_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuBfiW_WTyRCjiNePezPop4j9QGCOkz68YNMPRhRu1fMVWzgItVDsALH4pRnidHUjQgywuEHvNR8ze_1VGBrZrA3rn8ARj47fI5p6uVLmiWaOC6WIU9O-eqdVmb5EfJ2N7YH6WYOYm-el7G28elk70IzRIM26cpbpSVFSzPwblOUOCTKTUlGPVdNBGoXKrKvEcWbnVxIWL9d84y9tEiCdCNhBVHNvjAGIpMkBr6ckwIp_m-vvLIMAmA'

    @property
    def coverflow_2(self):
        if self.coverflow_card_2_url and self.coverflow_card_2_url.strip():
            return self.coverflow_card_2_url.strip()
        if self.coverflow_card_2_image:
            try:
                return self.coverflow_card_2_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuCNPj-zu7tcX6-s8dGzgXSL1uMOkEDNA2AwG9ID-NEX-GKmqi2oaVuN6NKut8NAgm1jCG815bCJkw2DaSdQc2A8pwV-YV1fXakGxuxYJ2fPAw6C33SSpYh2kg__h_lzOhVcFtEZM4ZkW3qBGehNHsspih6lTcN9bbQj5oVZpFvOUwJJHDabdHDBN-DCf-EqoFDrxCJwh6EdiiA6JRJfXTpNysOAjYnksA8BZaFyOyIY7euJH7_FWcc'

    @property
    def coverflow_3(self):
        if self.coverflow_card_3_url and self.coverflow_card_3_url.strip():
            return self.coverflow_card_3_url.strip()
        if self.coverflow_card_3_image:
            try:
                return self.coverflow_card_3_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuCpWLaMHEgbC4_C1cno63yFYn-ZAiwq8fhl_WCgfjafYjSBRmnsvWc8XXTN5QNSqiPtxF7VAdcBKVyNRN8D44uF-XYX1CSN1pZSBPXuh5c8oUx2ijEbNIZsE2r5Zi2Rx70rL6pEeykovA6XKXsR9384MuJJkSHITcWe9-YQU4C9Ptr6384CaR1zkWzPsa1Mw-RkjfFuB4jN7dmo-7OiTf7C_LJBBawCwqaruN5scXLPhLkONk_ZGpQ'

    @property
    def coverflow_4(self):
        if self.coverflow_card_4_url and self.coverflow_card_4_url.strip():
            return self.coverflow_card_4_url.strip()
        if self.coverflow_card_4_image:
            try:
                return self.coverflow_card_4_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuBP6Sc2G1ga1CiPRkIPjlFaE4nLFkuJKMJufcJ3XraTvuqM70_TjdbaX8DqUYVLYrbmH0bdrorwT6ULYwBOMmsfEuxDN2bqvx5wd72KCTjWKKh1XJSFqLVOMTEvNJTGmwuYIHMqrRYmHhpV6dBbP5hVhEVg9PPIyzvgYJb-RBcwvZb1ZR7xelUEL26wh_OZzoxcaYT7s5lRoW5rq5sMFtjDaUehA94PJRn4LO8MVcFANFFBp_JrB-w'

    @property
    def coverflow_5(self):
        if self.coverflow_card_5_url and self.coverflow_card_5_url.strip():
            return self.coverflow_card_5_url.strip()
        if self.coverflow_card_5_image:
            try:
                return self.coverflow_card_5_image.url
            except Exception:
                pass
        return 'https://lh3.googleusercontent.com/aida-public/AB6AXuAeX-7-m4xsZYUC1QI8Uul1nEoQ3G4b-o0GbQrVoGzRA1X56EcWlz-F5_KbtccY4AOAzW6RtFfqG-7VBfxqbnvfLXgiIgtKWgzDzBpa3Ix503c-nFY2APbz9Dkr-xxRAR_Sy4NwKzkvBr0-aUe4_bIOw3EALXmwSX7VmYGOzm8fX5_uF-WUF0Ame1zwakgBIZBlUOzuqpz3abxrpBxnffu2t4knM5FSJqDqUCUfjCrBCaDHT5hqUEM'


class FooterPage(models.Model):
    """
    Managed Content Page for Footer & Policies:
    1. Contact Us (/contact-us)
    2. Terms & Conditions (/terms-and-conditions)
    3. Privacy Policy (/privacy-policy)
    4. Refunds & Cancellations (/refunds-cancellations)
    5. Shipping & Delivery Policy (/shipping-policy)
    6. Payment & Installment Policy (/payment-installment-policy)
    """
    STATUS_CHOICES = [
        ('published', 'Published'),
        ('draft', 'Draft / Unsaved Revisions'),
        ('unpublished', 'Unpublished'),
    ]

    slug = models.SlugField(max_length=100, unique=True, help_text="URL slug identifier")
    title = models.CharField(max_length=200, help_text="Published page title")
    nav_label = models.CharField(max_length=100, help_text="Label in footer navigation")
    icon = models.CharField(max_length=50, default="📜", help_text="Emoji or icon symbol")
    short_description = models.CharField(max_length=300, blank=True, default="", help_text="Admin description")
    summary = models.TextField(blank=True, default="", help_text="Published page introduction")

    # Draft / Work-in-progress content
    draft_title = models.CharField(max_length=200, blank=True, default="")
    draft_nav_label = models.CharField(max_length=100, blank=True, default="")
    draft_summary = models.TextField(blank=True, default="")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    is_published = models.BooleanField(default=True)
    is_in_footer = models.BooleanField(default=True, help_text="Show in public footer")
    footer_order = models.PositiveIntegerField(default=1)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.CharField(max_length=150, blank=True, default="Master Admin")

    class Meta:
        ordering = ['footer_order', 'id']
        verbose_name = 'Footer Content Page'
        verbose_name_plural = 'Footer Content Pages'

    def __str__(self):
        return f"{self.title} (/{self.slug})"

    def get_absolute_url(self):
        return f"/{self.slug}/"

    @property
    def active_title(self):
        return self.title or self.draft_title

    @property
    def active_summary(self):
        return self.summary or self.draft_summary

    @classmethod
    def seed_default_pages(cls):
        """
        Seeds the exact six required content pages with professional, comprehensive,
        real business content for Glory Furniture Hub if they don't already exist.
        """
        from django.utils import timezone
        now = timezone.now()

        pages_data = [
            {
                'slug': 'contact-us',
                'title': 'Contact Us',
                'nav_label': 'Contact Us',
                'icon': '📞',
                'footer_order': 1,
                'short_description': 'Studio workshop address, direct customer support, phone, email & consultation hours.',
                'summary': 'Connect directly with Glory Furniture Hub’s master craftsmen, customer care studio, and workshop consultants in Hyderabad for custom orders, measurements, and order tracking.',
                'sections': [
                    {
                        'heading': '1. Workshop & Studio Location',
                        'content': '<p>Our primary woodworking studio and atelier is based in Hyderabad, Telangana. We welcome patrons, architects, and interior designers by appointment for timber grain inspection, live carving observation, and bespoke consultations.</p><p><strong>Workshop Address:</strong> Glory Furniture Hub, Workshop & Atelier Suite, Hyderabad, Telangana, India.</p>'
                    },
                    {
                        'heading': '2. Direct Support Channels',
                        'content': '<p>For order inquiries, delivery coordination, or custom furniture quotations, you can reach our team via:</p><ul><li><strong>Support Email:</strong> support@gloryfurniturehub.com</li><li><strong>Direct Phone:</strong> +91 95159 12524</li><li><strong>WhatsApp Concierge:</strong> +91 95159 12524</li></ul><p>Our support lines are open Monday through Saturday, from 10:00 AM to 7:30 PM IST.</p>'
                    },
                    {
                        'heading': '3. Custom Design Consultations',
                        'content': '<p>If you have specific architectural blueprints or require custom-dimensioned pieces, you may submit your reference photos and room dimensions through our Custom Request portal or schedule an in-home measurement visit with our field carpenter.</p>'
                    }
                ]
            },
            {
                'slug': 'terms-and-conditions',
                'title': 'Terms & Conditions',
                'nav_label': 'Terms & Conditions',
                'icon': '📜',
                'footer_order': 2,
                'short_description': 'Terms of sale, solid wood characteristics, order commitments, warranty and legal conditions.',
                'summary': 'These Terms & Conditions govern all purchases, custom joinery commissions, online orders, and customer relations with Glory Furniture Hub.',
                'sections': [
                    {
                        'heading': '1. Craftsmanship & Natural Wood Characteristics',
                        'content': '<p>All Glory Furniture Hub furniture is handcrafted from genuine, seasoned, kiln-dried Burma and CP Teak Wood. Because solid wood is an authentic organic material, subtle variations in natural grain patterns, knots, growth rings, and warm timber tone nuances are inherent signatures of genuine timber and are not defects.</p>'
                    },
                    {
                        'heading': '2. Custom Commissions & Blueprint Approvals',
                        'content': '<p>For bespoke orders with custom dimensions, fabric selection, or wood finishes, production commences once the customer confirms specifications. Customers are responsible for verifying room clearance and doorway access dimensions prior to dispatch.</p>'
                    },
                    {
                        'heading': '3. Pricing, GST & Taxes',
                        'content': '<p>All listed prices are denominated in Indian Rupees (INR) and are inclusive of 18% Goods & Services Tax (GST) as mandated by Indian law. Invoices with GST breakdown are provided upon order confirmation.</p>'
                    },
                    {
                        'heading': '4. 10-Year Joinery & Anti-Termite Warranty',
                        'content': '<p>Every Glory solid teak piece includes our structural warranty covering mortise-and-tenon frame integrity and kiln-treatment anti-borer protection. Warranty covers normal residential use and excludes accidental physical damage, improper outdoor exposure, or unauthorized structural modifications.</p>'
                    }
                ]
            },
            {
                'slug': 'privacy-policy',
                'title': 'Privacy Policy',
                'nav_label': 'Privacy Policy',
                'icon': '🛡️',
                'footer_order': 3,
                'short_description': 'Customer data protection, delivery address confidentiality, payment gateway security and rights.',
                'summary': 'At Glory Furniture Hub, we treat your personal privacy and transactional security with the highest standard of care.',
                'sections': [
                    {
                        'heading': '1. Information We Collect',
                        'content': '<p>We collect personal information necessary to fulfill your orders, provide white-glove delivery, and maintain customer accounts. This includes your name, delivery address, phone number, email address, and order history.</p>'
                    },
                    {
                        'heading': '2. Payment Security & Tokenization',
                        'content': '<p>We do not store complete credit card numbers, debit card PINs, or UPI passwords on our servers. All online transactions are processed through Cashfree Payments India Private Limited using 256-bit SSL encryption and RBI-compliant tokenized gateway infrastructure.</p>'
                    },
                    {
                        'heading': '3. Use of Delivery & Location Data',
                        'content': '<p>Your delivery address and phone number are used strictly by our logistics team and white-glove transport partners to coordinate route dispatch and safe installation. We never sell, rent, or trade your personal information to third-party marketing companies.</p>'
                    },
                    {
                        'heading': '4. Data Retention & Customer Rights',
                        'content': '<p>You may view, update, or request deletion of your saved addresses and account data at any time through your Profile dashboard or by contacting support@gloryfurniturehub.com.</p>'
                    }
                ]
            },
            {
                'slug': 'refunds-cancellations',
                'title': 'Refunds & Cancellations',
                'nav_label': 'Refunds & Cancellations',
                'icon': '↩️',
                'footer_order': 4,
                'short_description': 'Cancellation windows, transit damage protocols, customized product terms and refund processing.',
                'summary': 'Clear and transparent policies governing order cancellations, damaged-product claims, returns, and refund processing.',
                'sections': [
                    {
                        'heading': '1. Order Cancellation Window',
                        'content': '<p>Standard catalog orders may be cancelled within 24 hours of order placement for a full 100% refund without deduction, before raw timber cutting and preliminary joinery have begun.</p>'
                    },
                    {
                        'heading': '2. Customized & Bespoke Furniture',
                        'content': '<p>Custom orders built to non-standard dimensions, bespoke carvings, or custom upholstery fabrics cannot be cancelled after raw timber has been tailored and machined (after 48 hours of design sign-off). Partial refunds may be considered on a case-by-case basis subject to material recovery costs.</p>'
                    },
                    {
                        'heading': '3. Damaged or Defective on Delivery Claims',
                        'content': '<p>Our White-Glove delivery personnel unpack and assemble your furniture at your residence. Please inspect the piece upon arrival. In the rare event of transit damage or structural defect, report it immediately to the delivery team or within 48 hours with photographs. We will repair, replace the affected component, or provide a full replacement at our expense.</p>'
                    },
                    {
                        'heading': '4. Refund Timelines & Mode of Payment',
                        'content': '<p>Approved refunds are credited back to the original payment source (Bank Account, UPI, or Credit/Debit Card) via our payment gateway within 5 to 7 business days from approval date.</p>'
                    }
                ]
            },
            {
                'slug': 'shipping-policy',
                'title': 'Shipping & Delivery Policy',
                'nav_label': 'Shipping & Delivery Policy',
                'icon': '🚚',
                'footer_order': 5,
                'short_description': 'White-glove assembly in Hyderabad, pan-India insured freight, packaging and delivery timelines.',
                'summary': 'Comprehensive guidelines on our white-glove delivery, pan-India transport packaging, delivery schedules, and home clearance requirements.',
                'sections': [
                    {
                        'heading': '1. White-Glove In-Home Delivery (Hyderabad)',
                        'content': '<p>For orders within the Hyderabad and Secunderabad metropolitan area, Glory Furniture Hub provides premium White-Glove delivery. Our trained delivery team transports, brings the furniture into your room of choice, unpacks, and performs complete assembly at zero additional charge.</p>'
                    },
                    {
                        'heading': '2. Pan-India Delivery Coverage',
                        'content': '<p>We ship securely across India to major cities and regional hubs. Furniture is encased in multi-layered heavy corrugated wrap, foam edge guards, and reinforced wooden crating to guarantee zero transit damage during freight transport.</p>'
                    },
                    {
                        'heading': '3. Dispatch & Manufacturing Timelines',
                        'content': '<p>Standard in-stock atelier pieces are dispatched within 5 to 7 business days. Custom architectural creations or large suites requiring custom seasoning and carving typically require 2 to 4 weeks for complete artisanal fabrication and curing.</p>'
                    },
                    {
                        'heading': '4. Access & Dimension Verification',
                        'content': '<p>Please ensure that doorways, hallways, stairwells, and service elevators have adequate clearance for large solid pieces such as king beds, 8-seater dining tables, and 3-seater sofas before delivery day.</p>'
                    }
                ]
            },
            {
                'slug': 'payment-installment-policy',
                'title': 'Payment & Installment Policy',
                'nav_label': 'Payment & Installment Policy',
                'icon': '💳',
                'footer_order': 6,
                'short_description': 'Cashfree gateway integration, UPI, cards, 3 Equal Installments schedule and payment milestones.',
                'summary': 'Detailed explanation of our secure payment gateways, full upfront payment benefits, and flexible 3 Equal Installments plan.',
                'sections': [
                    {
                        'heading': '1. Supported Payment Methods',
                        'content': '<p>Glory Furniture Hub accepts all major digital payment options through our official Cashfree Payment Gateway:</p><ul><li><strong>UPI:</strong> Google Pay, PhonePe, Paytm, BHIM and direct VPA IDs.</li><li><strong>Cards:</strong> Visa, MasterCard, RuPay, and American Express debit and credit cards.</li><li><strong>Net Banking:</strong> Over 50 Indian commercial and private banks.</li><li><strong>Cash on Delivery (COD):</strong> Available for select verified orders with doorstep payment option.</li></ul>'
                    },
                    {
                        'heading': '2. Option A: 100% Full Payment Upfront',
                        'content': '<p>Settle the total order upfront in a single secure transaction. Benefits include immediate dispatch priority, expedited manufacturing queue, and zero future payment reminders or balance milestones.</p>'
                    },
                    {
                        'heading': '3. Option B: 3 Equal Installments Plan',
                        'content': '<p>To make fine solid wood furniture accessible, we offer an interest-free 3 Equal Installments option for eligible handcrafted pieces:</p><ul><li><strong>Installment 1 (Due Today):</strong> Exactly 33.33% paid at checkout to confirm and lock in your kiln timber batch.</li><li><strong>Installment 2 (Milestone 2):</strong> Exactly 33.33% due midway through the artisanal crafting schedule (typically day 15).</li><li><strong>Installment 3 (Final Milestone):</strong> Remaining 33.34% due upon dispatch or completion of polishing (day 30).</li></ul>'
                    },
                    {
                        'heading': '4. Installment Reminders & Outstanding Balances',
                        'content': '<p>Automated reminders with secure direct-payment links are sent via SMS and Email prior to each due date. Furniture dispatch is scheduled once all installment obligations are completed or as agreed upon in the order contract.</p>'
                    }
                ]
            }
        ]

        for pdata in pages_data:
            page, created = cls.objects.get_or_create(
                slug=pdata['slug'],
                defaults={
                    'title': pdata['title'],
                    'nav_label': pdata['nav_label'],
                    'icon': pdata['icon'],
                    'footer_order': pdata['footer_order'],
                    'short_description': pdata['short_description'],
                    'summary': pdata['summary'],
                    'draft_title': pdata['title'],
                    'draft_nav_label': pdata['nav_label'],
                    'draft_summary': pdata['summary'],
                    'status': 'published',
                    'is_published': True,
                    'is_in_footer': True,
                    'published_at': now,
                    'last_updated_by': 'Master Studio Admin',
                }
            )
            # Seed sections if new page or no sections
            if created or not page.sections.exists():
                for s_idx, sec_data in enumerate(pdata['sections'], start=1):
                    FooterPageSection.objects.create(
                        page=page,
                        heading=sec_data['heading'],
                        content=sec_data['content'],
                        draft_heading=sec_data['heading'],
                        draft_content=sec_data['content'],
                        order=s_idx,
                        is_active=True
                    )


class FooterPageSection(models.Model):
    """
    Individual section/paragraph of a FooterPage.
    Enables administrators to edit individual paragraphs, add/remove/reorder sections
    with separate draft and published content.
    """
    page = models.ForeignKey(FooterPage, on_delete=models.CASCADE, related_name='sections')
    heading = models.CharField(max_length=255, help_text="Published section heading")
    content = models.TextField(help_text="Published section text/HTML paragraphs")

    # Draft / Work-in-progress content
    draft_heading = models.CharField(max_length=255, blank=True, default="")
    draft_content = models.TextField(blank=True, default="")

    order = models.PositiveIntegerField(default=1, help_text="Display order sequence")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Footer Page Section'
        verbose_name_plural = 'Footer Page Sections'

    def __str__(self):
        return f"{self.page.slug} - Sec {self.order}: {self.heading[:40]}"

    @property
    def active_heading(self):
        return self.heading or self.draft_heading

    @property
    def active_content(self):
        return self.content or self.draft_content



