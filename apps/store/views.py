from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, Category, Review

def catalog_view(request):
    category_param = request.GET.get('category', 'All').strip()
    style_param = request.GET.get('style', 'All').strip()
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'popular').strip()
    max_price_param = request.GET.get('max_price')
    in_stock_only = request.GET.get('in_stock', 'false').lower() == 'true'

    products = Product.objects.all()

    # Category Filter
    if category_param and category_param != 'All':
        cat_lower = category_param.lower()
        if 'dining table' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Dining Table') |
                Q(category__slug='dining-table') |
                (Q(name__icontains='Dining Table') | (Q(name__icontains='Table') & Q(name__icontains='Dining')))
            ).exclude(name__icontains='Chairs')
        elif 'dining chair' in cat_lower or 'chairs' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Dining Chairs') |
                Q(category__slug='dining-chairs') |
                Q(name__icontains='Chair')
            )
        elif 'bed' in cat_lower or 'cot' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Bed') |
                Q(category__name__icontains='Cot') |
                Q(category__slug='cot-bed') |
                Q(name__icontains='Bed') |
                Q(name__icontains='Cot')
            )
        elif 'dressing' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Dressing') |
                Q(category__slug='dressing-table') |
                Q(name__icontains='Dressing') |
                Q(name__icontains='Vanity')
            )
        elif 'sofa' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Sofa') |
                Q(category__slug='sofa-set') |
                Q(name__icontains='Sofa') |
                Q(name__icontains='Couch')
            )
        elif 'headboard' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Headboard') |
                Q(category__slug='headboard') |
                Q(name__icontains='Headboard')
            )
        elif 'mandir' in cat_lower or 'pooja' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Mandir') |
                Q(category__slug='pooja-mandir') |
                Q(name__icontains='Mandir') |
                Q(name__icontains='Pooja') |
                Q(name__icontains='Temple')
            )
        elif 'podime' in cat_lower:
            products = products.filter(
                Q(category__name__icontains='Podimes') |
                Q(category__slug='podimes') |
                Q(name__icontains='Podimes') |
                Q(name__icontains='Peeta')
            )
        else:
            products = products.filter(
                Q(category__name__iexact=category_param) |
                Q(category__slug__iexact=category_param)
            )

    # Style Filter
    if style_param and style_param != 'All':
        products = products.filter(style__iexact=style_param)

    # Search Query
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(material__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Max Price
    max_price_val = 250000
    if max_price_param:
        try:
            val = float(max_price_param)
            if val < 250000:
                products = products.filter(price__lte=val)
                max_price_val = int(val)
        except ValueError:
            pass

    # In-Stock Filter
    if in_stock_only:
        products = products.filter(in_stock=True)

    # Sorting
    if sort_by in ['price_asc', 'price-low']:
        products = products.order_by('price')
    elif sort_by in ['price_desc', 'price-high']:
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating')
    else: # popular / featured
        products = products.order_by('-featured', '-rating')

    categories = Category.objects.all().order_by('order', 'name')
    styles = ['All', 'Classic', 'Modern Minimalist', 'Rustic', 'Traditional']

    try:
        product_list = list(products)
        cat_list = list(categories)
        total_count = len(product_list)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Database query error in catalog_view: %s", e)
        product_list = []
        cat_list = []
        total_count = 0

    wishlist_ids = []
    try:
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.wishlist_ids:
            wishlist_ids = request.user.profile.wishlist_ids
        else:
            wishlist_ids = request.session.get('glory_wishlist', [])
        wishlist_ids = [int(x) for x in wishlist_ids if str(x).isdigit()]
    except Exception:
        wishlist_ids = []

    cart_items = []
    try:
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.cart_items:
            cart_items = request.user.profile.cart_items
        else:
            cart_items = request.session.get('glory_cart', [])
    except Exception:
        cart_items = []
    cart_count = len(cart_items) if isinstance(cart_items, list) else 0

    context = {
        'products': product_list,
        'categories': cat_list,
        'styles': styles,
        'selected_category': category_param,
        'selected_style': style_param,
        'search_query': search_query,
        'sort_by': sort_by,
        'max_price': max_price_val,
        'in_stock_only': in_stock_only,
        'total_count': total_count,
        'wishlist_ids': wishlist_ids,
        'wishlist_count': len(wishlist_ids),
        'cart_count': cart_count,
        'page_title': 'Furniture Catalog',
    }
    return render(request, 'store/catalog.html', context)


from .catalog_data import SHOWCASE_PRODUCTS, SHOWCASE_CATEGORIES

def get_or_create_showcase_product(pk=None, slug=None):
    product = None
    if pk is not None:
        try:
            product = Product.objects.filter(pk=pk).first()
        except Exception:
            product = None
    elif slug:
        try:
            product = Product.objects.filter(slug=slug).first()
        except Exception:
            product = None

    if product:
        return product

    # If not found in DB, check SHOWCASE_PRODUCTS
    pdata = None
    target_id = None
    if pk is not None and int(pk) in SHOWCASE_PRODUCTS:
        target_id = int(pk)
        pdata = SHOWCASE_PRODUCTS[target_id]
    elif slug:
        for sid, sdata in SHOWCASE_PRODUCTS.items():
            if sdata.get('slug') == slug:
                pdata = sdata
                target_id = sid
                break
    elif pk is not None:
        try:
            target_id = int(pk)
            pdata = SHOWCASE_PRODUCTS.get(target_id, SHOWCASE_PRODUCTS.get(30))
        except (ValueError, TypeError):
            target_id = 30
            pdata = SHOWCASE_PRODUCTS.get(30)

    if not pdata:
        target_id = 30
        pdata = SHOWCASE_PRODUCTS.get(30)

    # Attempt to persist in DB
    try:
        cat_name = pdata.get('category_name')
        category = Category.objects.filter(name=cat_name).first()
        if not category:
            category, _ = Category.objects.get_or_create(
                name=cat_name or 'Furniture',
                defaults={'slug': (cat_name or 'furniture').lower().replace(' ', '-')}
            )

        defaults = {
            'name': pdata['name'],
            'slug': pdata.get('slug', f"product-{target_id}"),
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
        product, _ = Product.objects.update_or_create(id=target_id, defaults=defaults)
        return product
    except Exception as e:
        # Fallback to an in-memory Product instance if database write is restricted
        cat = Category(name=pdata.get('category_name', 'Living Room'), slug='living-room')
        prod = Product(
            id=target_id or 30,
            name=pdata['name'],
            slug=pdata.get('slug', f"product-{target_id or 30}"),
            category=cat,
            price=pdata['price'],
            rating=pdata.get('rating', 5.0),
            review_count=pdata.get('review_count', 1),
            material=pdata.get('material', 'Solid Teak Wood'),
            style=pdata.get('style', 'Classic'),
            dimensions=pdata.get('dimensions', 'Standard'),
            lead_time=pdata.get('lead_time', '5 - 7 Days Delivery'),
            description=pdata.get('description', ''),
            primary_image=pdata.get('primary_image', ''),
            secondary_images=pdata.get('secondary_images', []),
            featured=True,
            in_stock=True
        )
        return prod


def product_detail_view(request, pk=None, slug=None):
    product = get_or_create_showcase_product(pk=pk, slug=slug)
    if not product:
        product = Product.objects.first()
    if not product:
        product = get_or_create_showcase_product(pk=30)

    try:
        related = list(Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4])
        if len(related) < 4:
            others = list(Product.objects.exclude(pk=product.pk)[:8])
            for o in others:
                if o not in related and len(related) < 4:
                    related.append(o)
        related_products = related[:4]
    except Exception:
        related_products = []

    try:
        reviews = list(product.reviews.all().order_by('-created_at'))
    except Exception:
        reviews = []

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'page_title': product.name,
    }
    return render(request, 'store/product_detail.html', context)



def search_view(request):
    query = request.GET.get('q', '').strip()
    products = []
    if query:
        try:
            products = list(Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            ))
        except Exception:
            products = []

    recent_searches = ['Cot / Wooden Bed', 'Dining Table', 'Sofa Set', 'Pooja Mandir']
    popular_searches = ['Teak Cot', 'Dressing Table', 'Podimes', 'Headboard']

    context = {
        'query': query,
        'products': products,
        'recent_searches': recent_searches,
        'popular_searches': popular_searches,
    }
    return render(request, 'store/search.html', context)


def wishlist_view(request):
    if request.user.is_authenticated:
        from apps.accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        wishlist_ids = profile.wishlist_ids or request.session.get('glory_wishlist', [])
    else:
        wishlist_ids = request.session.get('glory_wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids)
    return render(request, 'store/wishlist.html', {'products': products})


def cart_view(request):
    if request.user.is_authenticated:
        from apps.accounts.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        cart = profile.cart_items or request.session.get('glory_cart', [])
    else:
        cart = request.session.get('glory_cart', [])

    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    gst = round(subtotal * 0.18, 2)
    total = subtotal + gst

    context = {
        'cart_items': cart,
        'subtotal': subtotal,
        'gst': gst,
        'total': total,
    }
    return render(request, 'store/cart.html', context)


@csrf_exempt
def cart_add_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_id = data.get('product_id')
            size = data.get('size', 'Standard')
            quantity = int(data.get('quantity', 1))
            if quantity < 1:
                return JsonResponse({'status': 'error', 'message': 'Quantity must be at least 1'}, status=400)
            if quantity > 50:
                return JsonResponse({'status': 'error', 'message': 'Maximum order quantity is 50 units'}, status=400)

            measurements = str(data.get('measurements') or data.get('custom_measurements') or '').strip()
            product = get_object_or_404(Product, pk=product_id)

            cart = request.session.get('glory_cart', [])
            # Check if item exists in cart
            existing = next((item for item in cart if item['id'] == product.id and item.get('size') == size), None)
            if existing:
                if existing['quantity'] + quantity > 50:
                    return JsonResponse({'status': 'error', 'message': 'Maximum 50 units allowed per item'}, status=400)
                existing['quantity'] += quantity
                if measurements:
                    existing['measurements'] = measurements
            else:
                cart.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'size': size,
                    'measurements': measurements,
                    'image': product.primary_image,
                    'material': product.material,
                })
            request.session['glory_cart'] = cart
            request.session.modified = True
            if request.user.is_authenticated:
                from apps.accounts.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.cart_items = cart
                profile.save(update_fields=['cart_items'])

            subtotal = sum(float(i['price']) * int(i.get('quantity', 1)) for i in cart)
            for item in cart:
                item['formatted_price'] = f"₹{int(float(item['price'])):,}"
                item['url'] = f"/product/{item['id']}/"
                item['booking_url'] = f"/booking-summary/?product={item['id']}"

            return JsonResponse({
                'status': 'success',
                'cart_count': len(cart),
                'cart': cart,
                'subtotal': subtotal,
                'formatted_subtotal': f"₹{int(subtotal):,}"
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@csrf_exempt
def cart_remove_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_id = int(data.get('product_id'))
            size = data.get('size')
            cart = request.session.get('glory_cart', [])
            cart = [i for i in cart if not (i['id'] == product_id and (not size or i.get('size') == size))]
            request.session['glory_cart'] = cart
            request.session.modified = True
            if request.user.is_authenticated:
                from apps.accounts.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.cart_items = cart
                profile.save(update_fields=['cart_items'])

            subtotal = sum(float(i['price']) * int(i.get('quantity', 1)) for i in cart)
            for item in cart:
                item['formatted_price'] = f"₹{int(float(item['price'])):,}"
                item['url'] = f"/product/{item['id']}/"
                item['booking_url'] = f"/booking-summary/?product={item['id']}"

            return JsonResponse({
                'status': 'success',
                'cart_count': len(cart),
                'cart': cart,
                'subtotal': subtotal,
                'formatted_subtotal': f"₹{int(subtotal):,}"
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def _serialize_wishlist_items(wishlist_ids):
    if not wishlist_ids:
        return []
    try:
        products = {p.id: p for p in Product.objects.filter(id__in=wishlist_ids).select_related('category')}
        items = []
        for pid in wishlist_ids:
            if pid in products:
                prod = products[pid]
                items.append({
                    'id': prod.id,
                    'name': prod.name,
                    'formatted_price': prod.formatted_price,
                    'primary_image': prod.primary_image,
                    'category': prod.category.name if prod.category else 'Solid Wood',
                    'material': prod.material or 'Solid Burma Teak',
                    'dimensions': prod.dimensions or 'Standard',
                    'rating': str(prod.rating) if hasattr(prod, 'rating') else '4.9',
                    'url': f"/product/{prod.id}/",
                })
        return items
    except Exception:
        return []


@csrf_exempt
def wishlist_toggle_api(request):
    wishlist = request.session.get('glory_wishlist', [])
    if request.method == 'GET':
        items = _serialize_wishlist_items(wishlist)
        return JsonResponse({'status': 'success', 'count': len(wishlist), 'items': items})

    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_id = int(data.get('product_id'))
            if product_id in wishlist:
                wishlist.remove(product_id)
                added = False
            else:
                wishlist.append(product_id)
                added = True
            request.session['glory_wishlist'] = wishlist
            request.session.modified = True
            if request.user.is_authenticated:
                from apps.accounts.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.wishlist_ids = wishlist
                profile.save(update_fields=['wishlist_ids'])
            items = _serialize_wishlist_items(wishlist)
            return JsonResponse({
                'status': 'success',
                'added': added,
                'count': len(wishlist),
                'items': items
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def location_lookup_api(request):
    import urllib.request
    pincode = request.GET.get('pincode', '').strip()
    lat = request.GET.get('lat', '').strip()
    lng = request.GET.get('lng', '').strip()

    # 1. Reverse Geocode via GPS Coordinates (Server-side, Zero-CORS)
    if lat and lng:
        try:
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lng}&localityLanguage=en"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                city = data.get('city') or data.get('locality') or data.get('principalSubdivision') or 'Local City'
                state = data.get('principalSubdivision') or 'India'
                pin = (data.get('postcode') or '').replace(' ', '')[:6]
                locality = data.get('locality') or ''
                return JsonResponse({
                    'status': 'success',
                    'city': city,
                    'locality': locality,
                    'state': state,
                    'pincode': pin,
                    'formatted': f"{locality + ', ' if locality else ''}{city}, {state}{f' (PIN: {pin})' if pin else ''}",
                    'lat': lat,
                    'lng': lng
                })
        except Exception:
            pass

    # 2. Pincode Lookup via India Post Official API (Server-side, Zero-CORS)
    if pincode and len(pincode) == 6 and pincode.isdigit():
        try:
            url = f"https://api.postalpincode.in/pincode/{pincode}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data and isinstance(data, list) and data[0].get('Status') == 'Success':
                    po_list = data[0].get('PostOffice', [])
                    if po_list:
                        po = po_list[0]
                        office = po.get('Name', '')
                        district = po.get('District', '')
                        state = po.get('State', '')
                        return JsonResponse({
                            'status': 'success',
                            'city': district,
                            'locality': office,
                            'state': state,
                            'pincode': pincode,
                            'formatted': f"{office + ', ' if office else ''}{district}, {state} (PIN: {pincode})",
                        })
        except Exception:
            pass

    # 3. Comprehensive Indian Postal Circle Prefix Lookup Table
    prefix_map = {
        '50': ('Hyderabad / Secunderabad', 'Telangana'),
        '51': ('Tirupati / Rayalaseema', 'Andhra Pradesh'),
        '52': ('Vijayawada / Guntur', 'Andhra Pradesh'),
        '53': ('Visakhapatnam / Coastal AP', 'Andhra Pradesh'),
        '56': ('Bengaluru Urban', 'Karnataka'),
        '57': ('Mangaluru / Mysuru', 'Karnataka'),
        '58': ('Hubballi-Dharwad', 'Karnataka'),
        '60': ('Chennai Central', 'Tamil Nadu'),
        '64': ('Coimbatore', 'Tamil Nadu'),
        '68': ('Kochi / Ernakulam', 'Kerala'),
        '40': ('Mumbai Metro', 'Maharashtra'),
        '41': ('Pune Central', 'Maharashtra'),
        '11': ('New Delhi Central', 'Delhi NCR'),
        '12': ('Gurugram / Faridabad', 'Haryana NCR'),
        '20': ('Noida / Ghaziabad', 'Uttar Pradesh NCR'),
        '70': ('Kolkata Metro', 'West Bengal'),
    }
    pref = pincode[:2] if len(pincode) >= 2 else ''
    if pref in prefix_map:
        city, state = prefix_map[pref]
        return JsonResponse({
            'status': 'success',
            'city': city,
            'state': state,
            'pincode': pincode,
            'formatted': f"{city}, {state} (PIN: {pincode})",
        })

    if pincode:
        return JsonResponse({
            'status': 'success',
            'city': 'Regional Delivery Hub',
            'state': 'India',
            'pincode': pincode,
            'formatted': f"Delivery Available (PIN: {pincode})",
        })

    return JsonResponse({'status': 'error', 'message': 'Pincode or coordinates required'}, status=400)

