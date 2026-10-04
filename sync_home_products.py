import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glory_furniture.settings')
django.setup()

from apps.store.models import Category, Product

# Ensure categories exist
categories_data = [
    ('Cot / Wooden Bed', 'cot-bed', 'Bedrooms', '/static/images/card_bed.jpg', 1),
    ('Dressing Table', 'dressing-table', 'Dressing', '/static/images/card_decor.jpg', 2),
    ('Sofa Set', 'sofa-set', 'Living Room', '/static/images/card_sofa.jpg', 3),
    ('Headboard', 'headboard', 'Bedrooms', '/static/images/card_bed.jpg', 4),
    ('Dining Table', 'dining-table', 'Dining', '/static/images/card_dining.jpg', 5),
    ('Dining Chairs', 'dining-chairs', 'Dining', '/static/images/card_dining.jpg', 6),
    ('Teapoy', 'teapoy', 'Living Room', '/static/images/card_office.jpg', 7),
    ('Pooja Mandir', 'pooja-mandir', 'Sacred Spaces', '/static/images/hero_epoxy_teak.jpg', 8),
    ('Podimes', 'podimes', 'Sacred & Cultural', '/static/images/card_office.jpg', 9),
]

cat_map = {}
for name, slug, room_type, img, order in categories_data:
    cat, _ = Category.objects.update_or_create(
        name=name,
        defaults={'slug': slug, 'room_type': room_type, 'image': img, 'order': order}
    )
    cat_map[name] = cat

products_info = [
    {
        'name': 'Royal Teak Wood Bed',
        'category': 'Cot / Wooden Bed',
        'price': 28999,
        'rating': 4.9,
        'review_count': 128,
        'material': 'Solid Kiln-Dried Burma Teak Wood',
        'style': 'Classic',
        'dimensions': '81" L × 74" W × 45" H (King Size 78"×72")',
        'lead_time': '3 - 5 Days Delivery',
        'description': 'Premium teak wood bed with elegant design and ultimate comfort for your home. Features hand-chiseled mortise-and-tenon joints and posture-slat support.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCNPj-zu7tcX6-s8dGzgXSL1uMOkEDNA2AwG9ID-NEX-GKmqi2oaVuN6NKut8NAgm1jCG815bCJkw2DaSdQc2A8pwV-YV1fXakGxuxYJ2fPAw6C33SSpYh2kg__h_lzOhVcFtEZM4ZkW3qBGehNHsspih6lTcN9bbQj5oVZpFvOUwJJHDabdHDBN-DCf-EqoFDrxCJwh6EdiiA6JRJfXTpNysOAjYnksA8BZaFyOyIY7euJH7_FWcc',
        'secondary_images': [
            'https://lh3.googleusercontent.com/aida/AEtjO1Ve42EmZZ8qT2ZyS6__mqtrzFES4W2oRX-7mDlivsziDazmoOZTiuCTNs_wM8z3oguAZzcWrNVk_RqvtBwplHFpOX1t_zVJmABnK0RuKJoSwLpwnROy3fDxgjLNXKaeEiY1iGV7E0tgaE0VIB9v4dBrJhxdODpAhdoP-gXLT3RCLERVswcVTiOunYfCkqJCa1AbJy7nfOtejkShEhrLArxUVm-PO7aXcT5xHYyUlW5gSWND29MgR_gQOA',
            'https://lh3.googleusercontent.com/aida/AEtjO1XW6wvd3HPw6lQROHuN3wTzkMY-Pnyw3G48vpR297ZoJsahlf94NmUilmd_ACYfzfZQByax2ItM0r7MKWITGTXhOhbL7HOnEeuAr8dZKHS_YTNu3Jc0d7rjE-s-YneQ7nBA29BnM6XOsYddNzVWn6ic8KCFkHUYNFj1C9PKXAdO2olI_UsvK9TbNl9Rpv015RUge0DHRCNukhPoxmiLYa1ZPPifNzfUU97mOjov13A-RvQK_jA2c6G-3g',
            'https://lh3.googleusercontent.com/aida/AEtjO1WecA0t0O-eg9gyhPLe0YKZMxCLAPl6_gitKv2MTZYJqHvHST3cCqbHoeHn-0GbMKfu2n_XvFtV83nUCDy8iBSLt4zTLNIO70J_8HfCWZHgqRtEZGEtJ5WlDgRJyuCIa51xqRm5EsNJyxyeswPXa1md1aUL6N52eyQXUJn2kcX6TlE9zx3NBnOU7g0yf2LUkvqTNUbVlnEfngFe0XlFUh-ul5PHvQYFhsnQtls3k7FtGkc1wYlRdeSt_Q'
        ],
        'featured': True,
    },
    {
        'name': 'Stockholm Curved Bouclé Sofa',
        'category': 'Sofa Set',
        'price': 48500,
        'rating': 4.9,
        'review_count': 94,
        'material': 'Textured Belgian Bouclé & Solid Oak Framing',
        'style': 'Modern Minimalist',
        'dimensions': '88" W × 38" D × 32" H',
        'lead_time': '5 - 7 Days Delivery',
        'description': 'Fluid sculptural sofa upholstered in textured off-white Belgian bouclé fabric with solid kiln-dried timber frame and high-density resilient cushioning.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBfiW_WTyRCjiNePezPop4j9QGCOkz68YNMPRhRu1fMVWzgItVDsALH4pRnidHUjQgywuEHvNR8ze_1VGBrZrA3rn8ARj47fI5p6uVLmiWaOC6WIU9O-eqdVmb5EfJ2N7YH6WYOYm-el7G28elk70IzRIM26cpbpSVFSzPwblOUOCTKTUlGPVdNBGoXKrKvEcWbnVxIWL9d84y9tEiCdCNhBVHNvjAGIpMkBr6ckwIp_m-vvLIMAmA',
        'secondary_images': [
            'https://lh3.googleusercontent.com/aida/AEtjO1VU3st2pJL0SOafKizs5fapLcuyZM_dh0cX7WpEjKm3iQ0ga_iTR8HSNkP1ec3x7ZyPO8hg5TQlyVQzm3UN32EOqw356eEAomaZSZwB4itSB21QxEdnXT371vjHUDWsrPKereKDUpppoU8f56CILXfd2YkI8Autne_M6BZZFN-H7NwLxrE9_FWPzLE7cKG-tIn1vqD6hLY3UDSrHRSBohi0Ut1FyA_Qt3nNlQqjI-KOTpZ95_q88_hV',
            'https://lh3.googleusercontent.com/aida/AEtjO1B7eqSPu3q8EzHg-WYsOBAtSE_NM76h_PuOXe0qJEw3pyGHmkorNmXhhH1HiAON7ohiwaLCi4COBafONdqQ2aJo36OcNEz6NCF9EqEWtN8xRCjRAC3cxta3NpkrcSzvY5G6yX_rYWExg88XCSq3NDcgSgrZB47f3LZCocAhu6xk-YNYvbibDCqYVPN2a--jcHpjoJDIAwaCziRHV6dq6cPxZcMZshUasYFJcrCH1w76-D8oZ8z9kplHNPts8gIy6oyd'
        ],
        'featured': True,
    },
    {
        'name': 'Kyoto Extendable Dining Table',
        'category': 'Dining Table',
        'price': 34200,
        'rating': 4.8,
        'review_count': 67,
        'material': 'Seasoned Natural Oak & Teak Timber',
        'style': 'Modern Minimalist',
        'dimensions': '72"-96" L × 38" W × 30" H (6 to 8 Seater)',
        'lead_time': '5 - 7 Days Delivery',
        'description': 'Minimalist Japanese dining table with precision butterfly-leaf extension and satin-smooth food-safe natural timber polish.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCpWLaMHEgbC4_C1cno63yFYn-ZAiwq8fhl_WCgfjafYjSBRmnsvWc8XXTN5QNSqiPtxF7VAdcBKVyNRN8D44uF-XYX1CSN1pZSBPXuh5c8oUx2ijEbNIZsE2r5Zi2Rx70rL6pEeykovA6XKXsR9384MuJJkSHITcWe9-YQU4C9Ptr6384CaR1zkWzPsa1Mw-RkjfFuB4jN7dmo-7OiTf7C_LJBBawCwqaruN5scXLPhLkONk_ZGpQ',
        'secondary_images': [
            'https://lh3.googleusercontent.com/aida/AEtjO1XLLUjRt17Ny6-HrngOfrDSBKzwlUNzviwSws6FIUBV8QcpVOYIRcN49Bk5CVEGC3Uiu0JeKZQj_8z4ayDsZVMy6Rn0TSWBGw90s1GwY78Bv1NXP16twUw3kKQm5q_sYXh9WQyBPI22IWNmdWZOUQLhj9iCpMauUxpGNRT6JD9RJ4SbVXzNHHNMPLwi6fITU_JN9qWIFz-dqJle-d7AplZKDkJKD9LMAxz7093MlxSe2gPBTQRVeO2zQw'
        ],
        'featured': True,
    },
    {
        'name': 'Imperial Arch Dressing Console',
        'category': 'Dressing Table',
        'price': 19800,
        'rating': 4.7,
        'review_count': 42,
        'material': 'Solid Burma Teak with Brass Accents & Tempered Mirror',
        'style': 'Classic',
        'dimensions': '48" W × 18" D × 72" H',
        'lead_time': '3 - 5 Days Delivery',
        'description': 'Arched mirror vanity console with soft-close velvet lined jewelry drawers, fluted timber detailing, and brass handles.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCHXbB_5yW0Y3h5w9Kj_Q5N-2hQyK8qjZ9Gv_8WJq1B2c8D4F3H7K9L2N4P6R8T0V2X4Z6B8D0F2H4J6L8N0P2R4T6V8X0Z2B4D6F8H0J2L4N6P8R',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Royal Carved Teak Diwan',
        'category': 'Podimes',
        'price': 31500,
        'rating': 4.9,
        'review_count': 76,
        'material': '100% Solid Grade-A Teak Wood',
        'style': 'Traditional',
        'dimensions': '75" L × 36" W × 28" H',
        'lead_time': '5 - 7 Days Delivery',
        'description': 'Traditional handcrafted solid teak diwan cot with intricate floral hand-carvings, side bolster supports, and durable timber planks.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBP6Sc2G1ga1CiPRkIPjlFaE4nLFkuJKMJufcJ3XraTvuqM70_TjdbaX8DqUYVLYrbmH0bdrorwT6ULYwBOMmsfEuxDN2bqvx5wd72KCTjWKKh1XJSFqLVOMTEvNJTGmwuYIHMqrRYmHhpV6dBbP5hVhEVg9PPIyzvgYJb-RBcwvZb1ZR7xelUEL26wh_OZzoxcaYT7s5lRoW5rq5sMFtjDaUehA94PJRn4LO8MVcFANFFBp_JrB-w',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Kyoto Walnut Platform Bed',
        'category': 'Cot / Wooden Bed',
        'price': 38900,
        'rating': 4.8,
        'review_count': 53,
        'material': 'American Walnut & Seasoned Teak',
        'style': 'Modern Minimalist',
        'dimensions': '80" L × 74" W × 36" H (Fits King Mattress 78"×72")',
        'lead_time': '5 - 7 Days Delivery',
        'description': 'Low-profile cantilever floating platform bed crafted in warm walnut timber with concealed LED glow channel and floating nightstands.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDeaFRiwZwCm1i5AVqC30S7jF8WM72meMr7Hz2M9GdKdVfcpLM3hyUU1JAnSln2F0X0OsM5kgSJyMoMhrK0eL23b4xMY2Jf_lCPMzOBiAm8fsCrf3y4kGxk54OAsG4C5_LZ0fqyZkgMPV-E1iMcANx6aQXlU8n2LD5OH8mZ-yrV7CRHQ2A3wTgDrdP5t_L9yogvqLPWr6v7x5YGlRyoTZfk4MCGUhsD4wipuHnm-VVgaUzgDq2b7is',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Atelier Belgian Linen Armchair',
        'category': 'Sofa Set',
        'price': 12499,
        'rating': 4.9,
        'review_count': 81,
        'material': 'Belgian Natural Linen & Teak Frame',
        'style': 'Modern Minimalist',
        'dimensions': '34" W × 36" D × 32" H',
        'lead_time': '3 - 5 Days Delivery',
        'description': 'Deep lounge armchair crafted with natural Belgian linen, tapered teak wood legs, and feather-down blend back cushion.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuB7eqSPu3q8EzHg-WYsOBAtSE_NM76h_PuOXe0qJEw3pyGHmkorNmXhhH1HiAON7ohiwaLCi4COBafONdqQ2aJo36OcNEz6NCF9EqEWtN8xRCjRAC3cxta3NpkrcSzvY5G6yX_rYWExg88XCSq3NDcgSgrZB47f3LZCocAhu6xk-YNYvbibDCqYVPN2a--jcHpjoJDIAwaCziRHV6dq6cPxZcMZshUasYFJcrCH1w76-D8oZ8z9kplHNPts8gIy6oyd',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Monolith Roman Travertine Teapoy',
        'category': 'Teapoy',
        'price': 24900,
        'rating': 4.9,
        'review_count': 62,
        'material': 'Honed Roman Travertine & Fluted Solid Teak',
        'style': 'Modern Minimalist',
        'dimensions': '48" L × 28" W × 16" H',
        'lead_time': '5 - 7 Days Delivery',
        'description': 'Solid honed Roman travertine coffee table resting on architectural fluted timber pedestals with zero-shine matte sealant.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuDs1CHnDgSpTW5dhn1BcIAfAhYFdyKxtizaWKBMPVorGediRIzcm_9eX3-Mo-6YbKcczGaVCXl0jBbVOnTnFBEClI5HyHTxfUoQCKdtafBvMn4idGDRHhQCuj5zWA4YVHPKSnBVzl76UN4J7qLiAtKriv_H8PFRghXYWApKM-gAYO0eKhOI_NisKFBnpWA8GuLpe9IVewf2AocrGe1rrSnRsJcx9VKRSKl9papqsUmDZdHJm1mqf-k',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Carved Teak Podium',
        'category': 'Podimes',
        'price': 16500,
        'rating': 4.8,
        'review_count': 35,
        'material': 'Hand-Carved Burma Teak',
        'style': 'Traditional',
        'dimensions': '24" W × 18" D × 46" H',
        'lead_time': '3 - 5 Days Delivery',
        'description': 'Distinguished presentation lectern crafted in seasoned teakwood with custom acoustic mic channel, book lip, and lockable storage.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuAeX-7-m4xsZYUC1QI8Uul1nEoQ3G4b-o0GbQrVoGzRA1X56EcWlz-F5_KbtccY4AOAzW6RtFfqG-7VBfxqbnvfLXgiIgtKWgzDzBpa3Ix503c-nFY2APbz9Dkr-xxRAR_Sy4NwKzkvBr0-aUe4_bIOw3EALXmwSX7VmYGOzm8fX5_uF-WUF0Ame1zwakgBIZBlUOzuqpz3abxrpBxnffu2t4knM5FSJqDqUCUfjCrBCaDHT5hqUEM',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Solid Rosewood Carved Teapoy',
        'category': 'Teapoy',
        'price': 14200,
        'rating': 4.7,
        'review_count': 49,
        'material': 'Seasoned Indian Rosewood (Sheesham) & Toughened Glass',
        'style': 'Classic',
        'dimensions': '42" L × 24" W × 18" H',
        'lead_time': '3 - 5 Days Delivery',
        'description': 'Artisan coffee table with curved cabriole legs, brass filigree inlays, lower magazine shelf, and 8mm tempered safety glass.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuCcpGfqb2W2mFXgsQ7WnS8TCUjZTyxcomjvPp-r9AS-FoD5TNSEfT448L6B7JByWsZO2RXvahPCZuBJ7d7GU31JBjbO12NHnTshd4AH_DTsZvxRVlKdrxIpVZtVzjy6qumIRh5o1QGM1uu2gG3VXjuPBcNXDRFZ1c_eRQoXRp0dip7yjPAeh2amxCZpT63WqzqiYYBMQOwRCRt9cz29mxZTtosSGI4WeoaL1h-eZywvtBil0IYc5cQ',
        'secondary_images': [],
        'featured': True,
    },
    {
        'name': 'Adolph Sheesham Wood Bed With Box Storage',
        'category': 'Cot / Wooden Bed',
        'price': 52999,
        'rating': 5.0,
        'review_count': 100,
        'material': 'Solid Kiln-Dried Sheesham & Teak Wood',
        'style': 'Classic',
        'dimensions': '81" L × 74" W × 45" H (Fits King Mattress 78"×72")',
        'lead_time': '3 - 5 Days Delivery',
        'description': 'Adolph Sheesham Wood Bed With Box Storage (King Size, Walnut Finish). German-engineered gas-strut hydraulic pistons, hand-woven natural rattan cane weave with emerald velvet plush cushioned backrest, and 2 matching teak modular bedside tables.',
        'primary_image': 'https://lh3.googleusercontent.com/aida-public/AB6AXuBCpo2r-u3S4r_DDwj9-UpN6jSORQRAG9WmDNK0aY4jUKohmmDmBkwwEl5V0xAF1RFzc5URtTHZm0hjB_gme5JnCRG-jLDklOJeXkPdUzj8eN5B6SF1QBWwMbqrSH9sQWGbgScsvcyzqXpgNwYnV5G-VLFToYS4ga2swhm73s3331KctMKpbabv1Clp3uUwElyZy8IpAWlh_vQ45HWb2jNrcSMghqVpqTrcLPBWx52RLfGI7QXh4ps',
        'secondary_images': [
            'https://lh3.googleusercontent.com/aida/AEtjO1Ve42EmZZ8qT2ZyS6__mqtrzFES4W2oRX-7mDlivsziDazmoOZTiuCTNs_wM8z3oguAZzcWrNVk_RqvtBwplHFpOX1t_zVJmABnK0RuKJoSwLpwnROy3fDxgjLNXKaeEiY1iGV7E0tgaE0VIB9v4dBrJhxdODpAhdoP-gXLT3RCLERVswcVTiOunYfCkqJCa1AbJy7nfOtejkShEhrLArxUVm-PO7aXcT5xHYyUlW5gSWND29MgR_gQOA',
            'https://lh3.googleusercontent.com/aida/AEtjO1XW6wvd3HPw6lQROHuN3wTzkMY-Pnyw3G48vpR297ZoJsahlf94NmUilmd_ACYfzfZQByax2ItM0r7MKWITGTXhOhbL7HOnEeuAr8dZKHS_YTNu3Jc0d7rjE-s-YneQ7nBA29BnM6XOsYddNzVWn6ic8KCFkHUYNFj1C9PKXAdO2olI_UsvK9TbNl9Rpv015RUge0DHRCNukhPoxmiLYa1ZPPifNzfUU97mOjov13A-RvQK_jA2c6G-3g',
            'https://lh3.googleusercontent.com/aida/AEtjO1WecA0t0O-eg9gyhPLe0YKZMxCLAPl6_gitKv2MTZYJqHvHST3cCqbHoeHn-0GbMKfu2n_XvFtV83nUCDy8iBSLt4zTLNIO70J_8HfCWZHgqRtEZGEtJ5WlDgRJyuCIa51xqRm5EsNJyxyeswPXa1md1aUL6N52eyQXUJn2kcX6TlE9zx3NBnOU7g0yf2LUkvqTNUbVlnEfngFe0XlFUh-ul5PHvQYFhsnQtls3k7FtGkc1wYlRdeSt_Q',
            'https://lh3.googleusercontent.com/aida-public/AB6AXuC5tmvhDvplR4JylTIAPO0xE2b5pCQER9BhzeiwQd-NoFfftA_KOk9YFLk3WXaZ3ZZKdggnfYoGigQbRkUiSYWGzix2n5BO8kI2qg_dRinzG1AOkw5UfhT4k851ohJwAfkdiWY_1lTV7r8P47A6TbYRKBM4tJ1utIOu_Uj2rkWhuaSlYCni6Eb7ma3tjE7lgn84u2IkFlTDsofZzMHGGlxHeBeFLj8WeclPe8-Ypcf2t06HgtL-p0V5LRwL4oHu8YxW'
        ],
        'featured': True,
    }
]

created_or_updated = []
for p_data in products_info:
    cat_name = p_data.pop('category')
    category = cat_map.get(cat_name)
    name = p_data.pop('name')
    
    prod, created = Product.objects.update_or_create(
        name=name,
        defaults={
            'category': category,
            **p_data
        }
    )
    status = 'Created' if created else 'Updated'
    print(f"{status}: ID {prod.id} - {prod.name} (Rs. {prod.price})")
    created_or_updated.append((prod.id, prod.name))

print("\nAll products synced successfully! Total in DB:", Product.objects.count())
