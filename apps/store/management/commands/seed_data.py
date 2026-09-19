from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.store.models import Category, Product, Review
from apps.bookings.models import Booking
from apps.custom_orders.models import CustomRequest
from apps.accounts.models import UserProfile, Notification
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seeds the database with authentic Glory Furniture Hub products, categories, reviews, and admin user'

    def handle(self, *args, **options):
        self.stdout.write("Starting Glory Furniture Hub database seeding...")

        # 1. Create Superuser if not exists
        if not User.objects.filter(username='admin').exists():
            u = User.objects.create_superuser('admin', 'admin@gloryfurniture.com', 'admin123')
            UserProfile.objects.create(
                user=u,
                full_name='Master Studio Admin',
                phone='',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS("Created admin superuser (admin / admin123)"))

        # 2. Categories
        categories_data = [
            ('Cot / Wooden Bed', 'cot-bed', 'Cot / Wooden Bed', '/static/images/card_bed.jpg', 1),
            ('Dressing Table', 'dressing-table', 'Dressing Table', '/static/images/card_decor.jpg', 2),
            ('Sofa Set', 'sofa-set', 'Sofa Set', '/static/images/card_sofa.jpg', 3),
            ('Headboard', 'headboard', 'Headboard', '/static/images/card_bed.jpg', 4),
            ('Dining Table', 'dining-table', 'Dining Table', '/static/images/card_dining.jpg', 5),
            ('Dining Chairs', 'dining-chairs', 'Dining Chairs', '/static/images/card_dining.jpg', 6),
            ('Pooja Mandir', 'pooja-mandir', 'Pooja Mandir', '/static/images/hero_epoxy_teak.jpg', 7),
            ('Podimes', 'podimes', 'Podimes', '/static/images/card_office.jpg', 8),
        ]

        cat_map = {}
        for name, slug, room_type, img, order in categories_data:
            cat, _ = Category.objects.update_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'room_type': room_type,
                    'image': img,
                    'order': order,
                }
            )
            cat_map[name] = cat
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(cat_map)} categories."))

        # 3. Products matching mockData.js exactly
        products_data = [
            {
                'id': 1,
                'name': 'Royal Walnut Cot / Wooden Bed',
                'category': 'Cot / Wooden Bed',
                'price': 99999,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 24,
                'material': 'Solid Teak & Walnut Wood',
                'style': 'Classic',
                'dimensions': '6/6 ft (King), 5/6 ft (Queen)',
                'lead_time': '7 - 10 Days Delivery',
                'description': 'Masterfully carved from premium kiln-dried solid teak and walnut. Features an arched headboard with warm hand-rubbed finish and reinforced posture-slat mattress support.',
                'finishes': ['Deep Walnut', 'Natural Honey', 'Warm Espresso'],
                'featured': True,
                'new_arrival': False,
                'primary_image': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1540518614846-7ede433c517a?auto=format&fit=crop&w=800&q=80',
                    'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': [
                    {'size': '6/6 ft (King)', 'price': 99999},
                    {'size': '5/6 ft (Queen)', 'price': 85000},
                    {'size': '4/6 ft (Double)', 'price': 72000},
                    {'size': '3/6 ft (Single)', 'price': 55000}
                ]
            },
            {
                'id': 2,
                'name': 'Heritage Teak Dining Table (6-Seater)',
                'category': 'Dining Table',
                'price': 68000,
                'in_stock': True,
                'rating': 4.8,
                'review_count': 19,
                'material': 'Solid Teak Wood',
                'style': 'Rustic',
                'dimensions': '200cm W × 100cm D × 76cm H',
                'lead_time': '5 - 7 Days Delivery',
                'description': 'Seats up to 6-8 guests comfortably. Crafted with traditional mortise-and-tenon joinery using sustainably sourced solid teak with natural water-resistant polish.',
                'finishes': ['Natural Teak', 'Matte Clear', 'Aged Bark'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1615066390971-03e4e1c36ddf?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': []
            },
            {
                'id': 3,
                'name': 'Maharaja Teak Wood Sofa Set (3+1+1)',
                'category': 'Sofa Set',
                'price': 78000,
                'in_stock': True,
                'rating': 5.0,
                'review_count': 32,
                'material': 'Solid Teak Frame & Organic Linen Cushions',
                'style': 'Classic',
                'dimensions': '3-Seater: 190cm W, 1-Seater: 85cm W',
                'lead_time': '7 - 10 Days Delivery',
                'description': 'Heavy-duty solid teak wood sofa set featuring exquisite hand-carved armrests, thick supportive high-density cushions, and washable linen velvet upholstery.',
                'finishes': ['Linen Cream', 'Emerald Green', 'Charcoal Slate'],
                'featured': True,
                'new_arrival': False,
                'primary_image': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1580481072645-022f9a6d8310?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': []
            },
            {
                'id': 4,
                'name': 'Artisan Teak Dressing Table with Mirror',
                'category': 'Dressing Table',
                'price': 42000,
                'in_stock': True,
                'rating': 4.8,
                'review_count': 16,
                'material': 'Solid Teak Wood & Beveled Glass Mirror',
                'style': 'Modern Minimalist',
                'dimensions': '110cm W × 45cm D × 180cm H',
                'lead_time': '5 - 7 Days Delivery',
                'description': 'Stunning full-height wooden dressing table equipped with a crystal-clear beveled mirror, 4 organizer drawers, and hidden LED border lighting.',
                'finishes': ['Natural Teak', 'Polished Rosewood Finish'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': []
            },
            {
                'id': 5,
                'name': 'Grand Hand-Carved Teak Pooja Mandir',
                'category': 'Pooja Mandir',
                'price': 54000,
                'in_stock': True,
                'rating': 5.0,
                'review_count': 28,
                'material': 'Pure Grade-A Teak Wood with Brass Bells',
                'style': 'Traditional',
                'dimensions': '90cm W × 45cm D × 135cm H',
                'lead_time': '5 - 7 Days Delivery',
                'description': 'Auspicious home temple masterfully sculpted with gopuram dome, traditional pillars, pull-out bhog tray, and pure brass temple bells.',
                'finishes': ['Traditional Honey Polish', 'Rich Teak Finish'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 6,
                'name': 'Handcrafted Floral Teak Headboard',
                'category': 'Headboard',
                'price': 26000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 15,
                'material': 'Solid Carved Teak Wood',
                'style': 'Classic',
                'dimensions': 'Fits King & Queen Cots',
                'lead_time': '3 - 5 Days Delivery',
                'description': 'Detailed relief wood carving headboard panel that mounts securely to any wall or standard cot frame to elevate your bedroom interior.',
                'finishes': ['Natural Teak', 'Aged Antique Finish'],
                'featured': False,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 7,
                'name': 'Teak Craft Dining Chairs (Set of 2)',
                'category': 'Dining Chairs',
                'price': 38000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 14,
                'material': 'Teak Wood & Woven Rattan',
                'style': 'Rustic',
                'dimensions': '48cm W × 52cm D × 88cm H',
                'lead_time': '3 - 5 Days Delivery',
                'description': 'Handcrafted dining chairs sculpted from solid teak with ergonomic curved backrests. Designed to pair with the Heritage Teak Dining Table.',
                'finishes': ['Natural Teak', 'Warm Honey'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1503602642458-232111445657?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 8,
                'name': 'Traditional Handcrafted Teak Podimes (Peeta Bench)',
                'category': 'Podimes',
                'price': 18000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 17,
                'material': 'Solid Burma Teak Wood',
                'style': 'Traditional',
                'dimensions': '120cm W × 50cm D × 45cm H',
                'lead_time': '3 Days Delivery',
                'description': 'A traditional South Indian wooden podimes / low diwan bench crafted from seasoned solid teak. Perfect for living areas, pooja rooms, and veranda seating.',
                'finishes': ['Glossy Honey Teak', 'Matte Teak Polish'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 9,
                'name': 'Carved Maharaja Teak Wood Bed / Cot',
                'category': 'Cot / Wooden Bed',
                'price': 115000,
                'in_stock': True,
                'rating': 5.0,
                'review_count': 31,
                'material': 'Pure Burma Teak Wood',
                'style': 'Traditional',
                'dimensions': '6/6 ft (King), 5/6 ft (Queen)',
                'lead_time': '7 - 10 Days Delivery',
                'description': 'Majestic king-sized wooden cot handcrafted by master wood artisans. Features intricately hand-chiseled floral cresting, solid pillars, and acoustic silent wooden base.',
                'finishes': ['Warm Honey', 'Deep Rosewood', 'Antique Teak'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1540518614846-7ede433c517a?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': [
                    {'size': '6/6 ft (King)', 'price': 115000},
                    {'size': '5/6 ft (Queen)', 'price': 98000},
                    {'size': '4/6 ft (Double)', 'price': 82000},
                    {'size': '3/6 ft (Single)', 'price': 62000}
                ]
            },
            {
                'id': 10,
                'name': 'Minimalist Low Platform Teak Bed',
                'category': 'Cot / Wooden Bed',
                'price': 89000,
                'in_stock': True,
                'rating': 4.8,
                'review_count': 18,
                'material': 'Kiln-Dried Solid Teak',
                'style': 'Modern Minimalist',
                'dimensions': '6/6 ft (King), 5/6 ft (Queen)',
                'lead_time': '5 - 7 Days Delivery',
                'description': 'Low-profile Japanese style platform bed with floating side rails and built-in hidden night ledges. Solid teak frame built to last generations.',
                'finishes': ['Natural Matte Teak', 'Smoked Walnut'],
                'featured': False,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': [
                    {'size': '6/6 ft (King)', 'price': 89000},
                    {'size': '5/6 ft (Queen)', 'price': 78000},
                    {'size': '4/6 ft (Double)', 'price': 65000},
                    {'size': '3/6 ft (Single)', 'price': 49000}
                ]
            },
            {
                'id': 11,
                'name': 'Royal Chesterfield Teak Sofa (3+2)',
                'category': 'Sofa Set',
                'price': 92000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 22,
                'material': 'Solid Teak Frame & Premium Micro-Suede',
                'style': 'Classic',
                'dimensions': '3-Seater: 205cm W, 2-Seater: 155cm W',
                'lead_time': '7 - 10 Days Delivery',
                'description': 'Deep button-tufted craftsmanship with exposed hand-polished teak legs and apron. Supreme comfort seating with 40-density HR foam.',
                'finishes': ['Royal Tan', 'Olive Forest', 'Ivory Cream'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1580481072645-022f9a6d8310?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [
                    'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80'
                ],
                'size_variants': []
            },
            {
                'id': 12,
                'name': 'Oval Grand Solid Teak Dining Table (8-Seater)',
                'category': 'Dining Table',
                'price': 88000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 20,
                'material': 'Grade-A Solid Teak Wood',
                'style': 'Classic',
                'dimensions': '240cm W × 110cm D × 76cm H',
                'lead_time': '7 - 10 Days Delivery',
                'description': 'Large oval banquet dining table with double fluted pedestal base. Seats 8 family members comfortably with heat-resistant satin lacquer.',
                'finishes': ['Natural Golden Teak', 'Dark Walnut'],
                'featured': True,
                'new_arrival': False,
                'primary_image': 'https://images.unsplash.com/photo-1577140917170-285929fb55b7?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 13,
                'name': 'Queen Anne Full-Mirror Teak Dressing Table',
                'category': 'Dressing Table',
                'price': 48000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 15,
                'material': 'Solid Teak Wood & High Clarity Glass',
                'style': 'Traditional',
                'dimensions': '120cm W × 48cm D × 190cm H',
                'lead_time': '5 - 7 Days Delivery',
                'description': 'Graceful cabriole legs, hand-carved floral accents, 5 velvet-lined jewelry drawers, and matching cushioned teak stool included.',
                'finishes': ['Polished Teak', 'Warm Honey'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 14,
                'name': 'Pillared Gopuram Teak Pooja Mandir (With Storage)',
                'category': 'Pooja Mandir',
                'price': 65000,
                'in_stock': True,
                'rating': 5.0,
                'review_count': 36,
                'material': 'Seasoned CP Teak Wood',
                'style': 'Traditional',
                'dimensions': '110cm W × 55cm D × 160cm H',
                'lead_time': '5 - 7 Days Delivery',
                'description': 'Large sacred shrine with 4 elephant-base pillars, tiered shikhar dome, dual pull-out diwali trays, and lockable storage cabinets.',
                'finishes': ['Temple Gold Teak', 'Natural Teak'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 15,
                'name': 'Heavy Carved Teak Podimes (Low Diwan Peeta)',
                'category': 'Podimes',
                'price': 24000,
                'in_stock': True,
                'rating': 4.8,
                'review_count': 12,
                'material': 'Heavy Solid Burma Teak',
                'style': 'Traditional',
                'dimensions': '140cm W × 60cm D × 48cm H',
                'lead_time': '3 Days Delivery',
                'description': 'Sturdy South Indian traditional seating bench with thick turned legs and carved floral borders. Ideal for living halls, prayer spaces, and traditional ceremonies.',
                'finishes': ['Aged Teak', 'Gloss Honey Teak'],
                'featured': True,
                'new_arrival': False,
                'primary_image': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            },
            {
                'id': 16,
                'name': 'Royal Arched Carved Teak Headboard',
                'category': 'Headboard',
                'price': 32000,
                'in_stock': True,
                'rating': 4.9,
                'review_count': 19,
                'material': 'Solid Teak Wood Panel',
                'style': 'Traditional',
                'dimensions': '185cm W × 10cm D × 110cm H',
                'lead_time': '3 - 5 Days Delivery',
                'description': 'Exquisite arched wooden headboard featuring hand-carved peacocks and floral vine motifs. Fits standard King and Queen bed cots.',
                'finishes': ['Natural Teak', 'Antique Walnut'],
                'featured': True,
                'new_arrival': True,
                'primary_image': 'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80',
                'secondary_images': [],
                'size_variants': []
            }
        ]

        for p_data in products_data:
            cat_obj = cat_map.get(p_data['category'])
            p, created = Product.objects.update_or_create(
                id=p_data['id'],
                defaults={
                    'name': p_data['name'],
                    'category': cat_obj,
                    'price': p_data['price'],
                    'in_stock': p_data['in_stock'],
                    'rating': p_data['rating'],
                    'review_count': p_data['review_count'],
                    'material': p_data['material'],
                    'style': p_data['style'],
                    'dimensions': p_data['dimensions'],
                    'lead_time': p_data['lead_time'],
                    'description': p_data['description'],
                    'finishes': p_data['finishes'],
                    'featured': p_data['featured'],
                    'new_arrival': p_data['new_arrival'],
                    'primary_image': p_data['primary_image'],
                    'secondary_images': p_data['secondary_images'],
                    'size_variants': p_data['size_variants'],
                }
            )
            # Add sample review
            if created or not p.reviews.exists():
                Review.objects.create(
                    product=p,
                    author='Ramesh V., Jubilee Hills',
                    rating=5,
                    comment='Outstanding Burma teak craftsmanship. The natural wood grain and satin polish look magnificent in our living space!'
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(products_data)} products with reviews."))

        # 4. Sample Bookings
        Booking.objects.get_or_create(
            booking_id='GLORY-BK-882194',
            defaults={
                'customer_name': 'Kavita Rao',
                'email': 'kavita.rao@example.com',
                'phone': '',
                'consultation_type': 'Showroom Visit',
                'preferred_date': timezone.now().date() + timedelta(days=3),
                'time_slot': '10:00 AM - 11:30 AM',
                'wood_preference': 'Pure Grade-A Burma Teak',
                'address': 'Plot 18, Banjara Hills Road 12, Hyderabad',
                'notes': 'Looking for 6-seater solid teak dining table and matching chairs.',
                'status': 'Confirmed'
            }
        )
        Booking.objects.get_or_create(
            booking_id='GLORY-BK-492015',
            defaults={
                'customer_name': 'Dr. Suresh Reddy',
                'email': 'suresh.reddy@example.com',
                'phone': '+91 98850 78901',
                'consultation_type': 'In-Home Site Measurement',
                'preferred_date': timezone.now().date() + timedelta(days=5),
                'time_slot': '02:00 PM - 03:30 PM',
                'wood_preference': 'Solid Burma Teak & Walnut',
                'address': 'Villa 45, Whisper Valley, Jubilee Hills',
                'notes': 'Master bedroom king cot with matching side tables and dressing table.',
                'status': 'Scheduled'
            }
        )

        # 5. Sample Custom Request
        CustomRequest.objects.get_or_create(
            request_id='GLORY-REQ-109284',
            defaults={
                'customer_name': 'Ananya Verma',
                'email': 'ananya.v@example.com',
                'phone': '+91 97012 34567',
                'category': 'Artisan Pooja Mandir',
                'wood_type': 'Pure Grade-A Burma Teak',
                'dimensions': '120cm W × 60cm D × 180cm H',
                'budget_range': '₹75,000 - ₹1,50,000',
                'description': 'Pooja mandir with tiered gopuram, peacock carvings, and brass bells with storage drawers.',
                'status': 'Estimation In Progress'
            }
        )

        self.stdout.write(self.style.SUCCESS("Glory Furniture Hub database seeded successfully 100%!"))
