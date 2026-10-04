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


BED_STORAGE_FALLBACKS = [
    # 0: Without Storage (Plain Platform)
    '/static/images/card_bed.jpg',
    # 1: Box Storage (Solid Plank Cavity)
    'https://lh3.googleusercontent.com/aida-public/AB6AXuBCpo2r-u3S4r_DDwj9-UpN6jSORQRAG9WmDNK0aY4jUKohmmDmBkwwEl5V0xAF1RFzc5URtTHZm0hjB_gme5JnCRG-jLDklOJeXkPdUzj8eN5B6SF1QBWwMbqrSH9sQWGbgScsvcyzqXpgNwYnV5G-VLFToYS4ga2swhm73s3331KctMKpbabv1Clp3uUwElyZy8IpAWlh_vQ45HWb2jNrcSMghqVpqTrcLPBWx52RLfGI7QXh4ps',
    # 2: Drawer Storage (Side Sliding Drawers)
    'https://lh3.googleusercontent.com/aida/AEtjO1XW6wvd3HPw6lQROHuN3wTzkMY-Pnyw3G48vpR297ZoJsahlf94NmUilmd_ACYfzfZQByax2ItM0r7MKWITGTXhOhbL7HOnEeuAr8dZKHS_YTNu3Jc0d7rjE-s-YneQ7nBA29BnM6XOsYddNzVWn6ic8KCFkHUYNFj1C9PKXAdO2olI_UsvK9TbNl9Rpv015RUge0DHRCNukhPoxmiLYa1ZPPifNzfUU97mOjov13A-RvQK_jA2c6G-3g',
    # 3: Hydraulic Storage (German Gas-Lift Pistons Open)
    'https://lh3.googleusercontent.com/aida-public/AB6AXuC5tmvhDvplR4JylTIAPO0xE2b5pCQER9BhzeiwQd-NoFfftA_KOk9YFLk3WXaZ3ZZKdggnfYoGigQbRkUiSYWGzix2n5BO8kI2qg_dRinzG1AOkw5UfhT4k851ohJwAfkdiWY_1lTV7r8P47A6TbYRKBM4tJ1utIOu_Uj2rkWhuaSlYCni6Eb7ma3tjE7lgn84u2IkFlTDsofZzMHGGlxHeBeFLj8WeclPe8-Ypcf2t06HgtL-p0V5LRwL4oHu8YxW',
]

DINING_CHAIR_FALLBACKS = [
    # 0: 6 Chairs (Standard Dining Suite - Cover)
    'https://lh3.googleusercontent.com/aida-public/AB6AXuCpWLaMHEgbC4_C1cno63yFYn-ZAiwq8fhl_WCgfjafYjSBRmnsvWc8XXTN5QNSqiPtxF7VAdcBKVyNRN8D44uF-XYX1CSN1pZSBPXuh5c8oUx2ijEbNIZsE2r5Zi2Rx70rL6pEeykovA6XKXsR9384MuJJkSHITcWe9-YQU4C9Ptr6384CaR1zkWzPsa1Mw-RkjfFuB4jN7dmo-7OiTf7C_LJBBawCwqaruN5scXLPhLkONk_ZGpQ',
    # 1: 2 Chairs (Bistro / Cafe 2-Seater)
    '/static/images/card_dining.jpg',
    # 2: 4 Chairs (Compact Family 4-Seater)
    'https://lh3.googleusercontent.com/aida/AEtjO1XLLUjRt17Ny6-HrngOfrDSBKzwlUNzviwSws6FIUBV8QcpVOYIRcN49Bk5CVEGC3Uiu0JeKZQj_8z4ayDsZVMy6Rn0TSWBGw90s1GwY78Bv1NXP16twUw3kKQm5q_sYXh9WQyBPI22IWNmdWZOUQLhj9iCpMauUxpGNRT6JD9RJ4SbVXzNHHNMPLwi6fITU_JN9qWIFz-dqJle-d7AplZKDkJKD9LMAxz7093MlxSe2gPBTQRVeO2zQw',
    # 3: 8 Chairs (Grand Manor 8-Seater Feast)
    'https://lh3.googleusercontent.com/aida/AEtjO1Ve42EmZZ8qT2ZyS6__mqtrzFES4W2oRX-7mDlivsziDazmoOZTiuCTNs_wM8z3oguAZzcWrNVk_RqvtBwplHFpOX1t_zVJmABnK0RuKJoSwLpwnROy3fDxgjLNXKaeEiY1iGV7E0tgaE0VIB9v4dBrJhxdODpAhdoP-gXLT3RCLERVswcVTiOunYfCkqJCa1AbJy7nfOtejkShEhrLArxUVm-PO7aXcT5xHYyUlW5gSWND29MgR_gQOA',
    # 4: 12 Chairs (Royal Banquet 12-Seater Feast)
    'https://lh3.googleusercontent.com/aida/AEtjO1WecA0t0O-eg9gyhPLe0YKZMxCLAPl6_gitKv2MTZYJqHvHST3cCqbHoeHn-0GbMKfu2n_XvFtV83nUCDy8iBSLt4zTLNIO70J_8HfCWZHgqRtEZGEtJ5WlDgRJyuCIa51xqRm5EsNJyxyeswPXa1md1aUL6N52eyQXUJn2kcX6TlE9zx3NBnOU7g0yf2LUkvqTNUbVlnEfngFe0XlFUh-ul5PHvQYFhsnQtls3k7FtGkc1wYlRdeSt_Q',
]


class Product(models.Model):
    STYLE_CHOICES = [
        ('Classic', 'Classic'),
        ('Modern Minimalist', 'Modern Minimalist'),
        ('Rustic', 'Rustic'),
        ('Traditional', 'Traditional'),
    ]

    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    review_count = models.PositiveIntegerField(default=1)
    material = models.CharField(max_length=250, default='Solid Teak Wood')
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='Classic')
    dimensions = models.CharField(max_length=250, default='Standard')
    lead_time = models.CharField(max_length=120, default='5 - 7 Days Delivery')
    installment_days = models.PositiveIntegerField(default=60, help_text="Total days for product completion and 3-installment payment schedule.")
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

        ctype = self.category_type
        if ctype in ['bed', 'diwan']:
            for fb in BED_STORAGE_FALLBACKS:
                if len(images) < 4 and fb not in images:
                    images.append(fb)
        elif ctype == 'dining':
            for fb in DINING_CHAIR_FALLBACKS:
                if len(images) < 5 and fb not in images:
                    images.append(fb)

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

    @property
    def category_type(self):
        n = (self.name or '').lower()
        c = (self.category.name if self.category else '').lower()
        if 'diwan' in n or 'divan' in n or 'podime' in c or 'podime' in n:
            return 'diwan'
        if 'bed' in n or 'cot' in n or 'bed' in c or 'cot' in c:
            return 'bed'
        if 'dining' in n or 'dining' in c:
            return 'dining'
        if 'sofa' in n or 'couch' in n or 'armchair' in n or 'sofa' in c:
            return 'sofa'
        if 'dressing' in n or 'vanity' in n or 'dressing' in c:
            return 'dressing'
        if 'teapoy' in n or 'coffee table' in n or 'teapoy' in c:
            return 'teapoy'
        return 'general'

    @property
    def size_config_list(self):
        if self.size_variants and isinstance(self.size_variants, list) and len(self.size_variants) > 0:
            return self.size_variants

        ctype = self.category_type
        base = int(self.price)
        if ctype == 'bed':
            return [
                {
                    'id': 'king',
                    'name': 'King Size (78" × 72")',
                    'subtitle': '78" × 72" Master Suite',
                    'dimensions': '81" L × 74" W × 45" H (Fits Mattress 78"×72")',
                    'delta': 0,
                    'price': base,
                    'is_default': True
                },
                {
                    'id': 'queen',
                    'name': 'Queen Size (78" × 60")',
                    'subtitle': '78" × 60" Compact Master',
                    'dimensions': '81" L × 62" W × 45" H (Fits Mattress 78"×60")',
                    'delta': -3000,
                    'price': max(1000, base - 3000),
                    'is_default': False
                },
                {
                    'id': 'single',
                    'name': 'Single Suite (78" × 36")',
                    'subtitle': '78" × 36" Studio & Kids Suite',
                    'dimensions': '81" L × 38" W × 40" H (Fits Mattress 78"×36")',
                    'delta': -8000,
                    'price': max(1000, base - 8000),
                    'is_default': False
                }
            ]
        elif ctype == 'diwan':
            return [
                {
                    'id': 'single_diwan',
                    'name': 'Single Diwan (75" × 36")',
                    'subtitle': '75" × 36" Living Daybed',
                    'dimensions': '78" L × 38" W × 28" H',
                    'delta': 0,
                    'price': base,
                    'is_default': True
                },
                {
                    'id': 'queen_diwan',
                    'name': 'Queen Diwan (78" × 48")',
                    'subtitle': '78" × 48" Grand Lounger',
                    'dimensions': '81" L × 50" W × 30" H',
                    'delta': 4500,
                    'price': base + 4500,
                    'is_default': False
                },
                {
                    'id': 'king_diwan',
                    'name': 'King Diwan (78" × 60")',
                    'subtitle': '78" × 60" Royal Diwan Bed',
                    'dimensions': '81" L × 62" W × 32" H',
                    'delta': 8500,
                    'price': base + 8500,
                    'is_default': False
                }
            ]
        elif ctype == 'dining':
            f = self.finishes if isinstance(self.finishes, dict) else {}
            d2 = int(f.get('dining_chair_2_delta', -14000))
            d4 = int(f.get('dining_chair_4_delta', -7000))
            d8 = int(f.get('dining_chair_8_delta', 15000))
            d12 = int(f.get('dining_chair_12_delta', 35000))

            all_imgs = self.all_images
            img_6 = all_imgs[0] if len(all_imgs) > 0 else DINING_CHAIR_FALLBACKS[0]
            img_2 = all_imgs[1] if len(all_imgs) > 1 else DINING_CHAIR_FALLBACKS[1]
            img_4 = all_imgs[2] if len(all_imgs) > 2 else DINING_CHAIR_FALLBACKS[2]
            img_8 = all_imgs[3] if len(all_imgs) > 3 else DINING_CHAIR_FALLBACKS[3]
            img_12 = all_imgs[4] if len(all_imgs) > 4 else DINING_CHAIR_FALLBACKS[4]

            return [
                {
                    'id': 'chairs_2',
                    'name': '2 Chairs (Bistro / Cafe Suite)',
                    'subtitle': '36" × 36" Table + 2 Teak Chairs',
                    'dimensions': '36" L × 36" W × 30" H',
                    'delta': d2,
                    'price': max(1000, base + d2),
                    'image': img_2,
                    'photo_index': 1,
                    'is_default': False
                },
                {
                    'id': 'chairs_4',
                    'name': '4 Chairs (Compact Family Suite)',
                    'subtitle': '48" × 36" Table + 4 Teak Chairs',
                    'dimensions': '48" L × 36" W × 30" H',
                    'delta': d4,
                    'price': max(1000, base + d4),
                    'image': img_4,
                    'photo_index': 2,
                    'is_default': False
                },
                {
                    'id': 'chairs_6',
                    'name': '6 Chairs (Standard Dining Suite)',
                    'subtitle': '72" × 38" Table + 6 Teak Chairs',
                    'dimensions': '72" L × 38" W × 30" H',
                    'delta': 0,
                    'price': base,
                    'image': img_6,
                    'photo_index': 0,
                    'is_default': True
                },
                {
                    'id': 'chairs_8',
                    'name': '8 Chairs (Grand Manor Suite)',
                    'subtitle': '96" × 42" Table + 8 Teak Chairs',
                    'dimensions': '96" L × 42" W × 30" H',
                    'delta': d8,
                    'price': base + d8,
                    'image': img_8,
                    'photo_index': 3,
                    'is_default': False
                },
                {
                    'id': 'chairs_12',
                    'name': '12 Chairs (Royal Banquet Suite)',
                    'subtitle': '132" × 46" Table + 12 Teak Chairs',
                    'dimensions': '132" L × 46" W × 30" H',
                    'delta': d12,
                    'price': base + d12,
                    'image': img_12,
                    'photo_index': 4,
                    'is_default': False
                }
            ]
        elif ctype == 'sofa':
            return [
                {
                    'id': 'sofa_1',
                    'name': '1-Seater Armchair',
                    'subtitle': '34" W × 36" D × 32" H Lounge Chair',
                    'dimensions': '34" W × 36" D × 32" H',
                    'delta': -int(base * 0.55),
                    'price': max(1000, int(base * 0.45)),
                    'is_default': False
                },
                {
                    'id': 'sofa_2',
                    'name': '2-Seater Loveseat',
                    'subtitle': '58" W × 36" D × 34" H Loveseat',
                    'dimensions': '58" W × 36" D × 34" H',
                    'delta': -int(base * 0.25),
                    'price': max(1000, int(base * 0.75)),
                    'is_default': False
                },
                {
                    'id': 'sofa_3',
                    'name': '3-Seater Sovereign',
                    'subtitle': '84" W × 38" D × 34" H Couch',
                    'dimensions': '84" W × 38" D × 34" H',
                    'delta': 0,
                    'price': base,
                    'is_default': True
                },
                {
                    'id': 'sofa_311',
                    'name': '3+1+1 (5-Seater Royal Suite)',
                    'subtitle': '3-Seater Couch + 2 Armchairs',
                    'dimensions': '84" W + Two 34" W Armchairs',
                    'delta': int(base * 0.65),
                    'price': int(base * 1.65),
                    'is_default': False
                },
                {
                    'id': 'sofa_lshape',
                    'name': 'L-Shape Sectional Suite',
                    'subtitle': '104" W × 68" Chaise × 34" H',
                    'dimensions': '104" W × 68" D (Chaise) × 34" H',
                    'delta': int(base * 0.5),
                    'price': int(base * 1.5),
                    'is_default': False
                }
            ]
        elif ctype == 'dressing':
            return [
                {
                    'id': 'dress_compact',
                    'name': 'Compact Slim Console (36")',
                    'subtitle': '36" W × 16" D × 70" H Studio Vanity',
                    'dimensions': '36" W × 16" D × 70" H',
                    'delta': -3500,
                    'price': max(1000, base - 3500),
                    'is_default': False
                },
                {
                    'id': 'dress_standard',
                    'name': 'Standard Arched Vanity (48")',
                    'subtitle': '48" W × 18" D × 72" H Arched Console',
                    'dimensions': '48" W × 18" D × 72" H',
                    'delta': 0,
                    'price': base,
                    'is_default': True
                },
                {
                    'id': 'dress_grand',
                    'name': 'Grand Royal Dressing Suite (60")',
                    'subtitle': '60" W × 20" D × 78" H Full Length Vanity',
                    'dimensions': '60" W × 20" D × 78" H',
                    'delta': 7500,
                    'price': base + 7500,
                    'is_default': False
                }
            ]
        elif ctype == 'teapoy':
            return [
                {
                    'id': 'teapoy_square',
                    'name': 'Compact Square Teapoy (24"×24")',
                    'subtitle': '24" L × 24" W × 18" H Accent Coffee Table',
                    'dimensions': '24" L × 24" W × 18" H',
                    'delta': -3500,
                    'price': max(1000, base - 3500),
                    'is_default': False
                },
                {
                    'id': 'teapoy_standard',
                    'name': 'Standard Rectangular (42"×24")',
                    'subtitle': '42" L × 24" W × 18" H Living Table',
                    'dimensions': '42" L × 24" W × 18" H',
                    'delta': 0,
                    'price': base,
                    'is_default': True
                },
                {
                    'id': 'teapoy_grand',
                    'name': 'Grand Architectural Teapoy (48"×28")',
                    'subtitle': '48" L × 28" W × 16" H Travertine / Oval Table',
                    'dimensions': '48" L × 28" W × 16" H',
                    'delta': 6000,
                    'price': base + 6000,
                    'is_default': False
                }
            ]
        else:
            return [
                {
                    'id': 'std',
                    'name': self.dimensions or 'Standard Specification',
                    'subtitle': 'Master Artisan Craftsmanship',
                    'dimensions': self.dimensions or 'Standard Specification',
                    'delta': 0,
                    'price': base,
                    'is_default': True
                }
            ]

    @property
    def storage_config_list(self):
        ctype = self.category_type
        if ctype not in ['bed', 'diwan']:
            return []

        all_imgs = self.all_images
        img_no_storage = all_imgs[0] if len(all_imgs) > 0 else BED_STORAGE_FALLBACKS[0]
        img_box = all_imgs[1] if len(all_imgs) > 1 else BED_STORAGE_FALLBACKS[1]
        img_drawers = all_imgs[2] if len(all_imgs) > 2 else BED_STORAGE_FALLBACKS[2]
        img_hydraulic = all_imgs[3] if len(all_imgs) > 3 else BED_STORAGE_FALLBACKS[3]

        # Read admin configured deltas if present
        f = self.finishes if isinstance(self.finishes, dict) else {}
        no_storage_delta = int(f.get('no_storage_delta', -5000))
        box_storage_delta = int(f.get('box_storage_delta', 0))
        drawer_storage_delta = int(f.get('drawer_storage_delta', 5500))
        hydraulic_storage_delta = int(f.get('hydraulic_storage_delta', 11000))

        def fmt_delta(d):
            if d == 0:
                return 'Standard'
            elif d > 0:
                return f"+₹{abs(d):,}"
            else:
                return f"-₹{abs(d):,}"

        return [
            {
                'id': 'no_storage',
                'name': 'Without Storage',
                'subtitle': 'Plain Slat Platform',
                'delta': no_storage_delta,
                'delta_label': fmt_delta(no_storage_delta),
                'description': 'Minimalist open timber framework with posture slats for natural air circulation.',
                'image': img_no_storage,
                'photo_index': 0,
                'is_default': False
            },
            {
                'id': 'box_storage',
                'name': 'Box Storage',
                'subtitle': 'Solid Plank Cavity',
                'delta': box_storage_delta,
                'delta_label': fmt_delta(box_storage_delta),
                'description': 'Heavy-duty manual plank lift partitions with deep solid wood underbed storage.',
                'image': img_box,
                'photo_index': 1,
                'is_default': True
            },
            {
                'id': 'drawer_storage',
                'name': 'Drawer Storage',
                'subtitle': 'Smooth Pull Drawers',
                'delta': drawer_storage_delta,
                'delta_label': fmt_delta(drawer_storage_delta),
                'description': 'Four heavy-duty ball-bearing side glide sliding drawers for quick linen access.',
                'image': img_drawers,
                'photo_index': 2,
                'is_default': False
            },
            {
                'id': 'hydraulic_storage',
                'name': 'Hydraulic Storage',
                'subtitle': 'German Gas-Lift Piston',
                'delta': hydraulic_storage_delta,
                'delta_label': fmt_delta(hydraulic_storage_delta),
                'description': 'Effortless German gas-strut hydraulic lift mechanism with 100% full underbed storage bay.',
                'image': img_hydraulic,
                'photo_index': 3,
                'is_default': False
            }
        ]

    @property
    def dining_plank_options(self):
        all_imgs = self.all_images
        img_rect = all_imgs[0] if len(all_imgs) > 0 else ''
        img_circle = all_imgs[1] if len(all_imgs) > 1 else img_rect
        img_square = all_imgs[2] if len(all_imgs) > 2 else img_rect
        return [
            {
                'id': 'rectangular_plank',
                'name': 'Rectangular Plank',
                'subtitle': 'Classic Long Grain',
                'description': 'Single-slab matched natural straight grain Burma teak top with eased pencil bevel edges.',
                'image': img_rect,
                'is_default': True
            },
            {
                'id': 'circle_plank',
                'name': 'Circle Plank',
                'subtitle': 'Round Beveled Edge',
                'description': 'Curved architectural circular timber tabletop encouraging communal dining and conversation.',
                'image': img_circle,
                'is_default': False
            },
            {
                'id': 'square_plank',
                'name': 'Square Plank',
                'subtitle': 'Architectural Cube Block',
                'description': 'Symmetric modern minimalist square top with solid end-grain timber stabilization.',
                'image': img_square,
                'is_default': False
            }
        ]

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.product.name} ({self.rating}★)"
