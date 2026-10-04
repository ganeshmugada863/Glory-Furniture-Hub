from django.db import migrations

def seed_products(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Product = apps.get_model('store', 'Product')

    from apps.store.catalog_data import SHOWCASE_CATEGORIES, SHOWCASE_PRODUCTS

    cat_map = {}
    for name, slug, room_type, img, order in SHOWCASE_CATEGORIES:
        cat, _ = Category.objects.update_or_create(
            name=name,
            defaults={'slug': slug, 'room_type': room_type, 'image': img, 'order': order}
        )
        cat_map[name] = cat

    for pid, pdata in SHOWCASE_PRODUCTS.items():
        cat_name = pdata.get('category_name')
        category = cat_map.get(cat_name)
        
        defaults = {
            'name': pdata['name'],
            'slug': pdata.get('slug', ''),
            'category': category,
            'price': pdata['price'],
            'rating': pdata.get('rating', 5.0),
            'review_count': pdata.get('review_count', 1),
            'material': pdata.get('material', 'Solid Teak Wood'),
            'style': pdata.get('style', 'Classic'),
            'dimensions': pdata.get('dimensions', 'Standard'),
            'lead_time': pdata.get('lead_time', '5 - 7 Days Delivery'),
            'description': pdata.get('description', ''),
            'primary_image': pdata.get('primary_image', ''),
            'secondary_images': pdata.get('secondary_images', []),
            'featured': pdata.get('featured', True),
            'in_stock': True,
        }

        # Check by ID first, then by name
        prod = Product.objects.filter(id=pid).first()
        if not prod:
            prod = Product.objects.filter(name=pdata['name']).first()

        if prod:
            for k, v in defaults.items():
                setattr(prod, k, v)
            prod.save()
        else:
            try:
                Product.objects.create(id=pid, **defaults)
            except Exception:
                Product.objects.create(**defaults)

    if schema_editor.connection.vendor == 'postgresql':
        try:
            with schema_editor.connection.cursor() as cursor:
                cursor.execute("SELECT setval(pg_get_serial_sequence('store_product', 'id'), coalesce(max(id), 1)) FROM store_product;")
        except Exception:
            pass

def unseed_products(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_category_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_products, reverse_code=unseed_products),
    ]
