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

    context = {
        'products': products,
        'categories': categories,
        'styles': styles,
        'selected_category': category_param,
        'selected_style': style_param,
        'search_query': search_query,
        'sort_by': sort_by,
        'max_price': max_price_val,
        'in_stock_only': in_stock_only,
        'total_count': products.count(),
        'page_title': 'Furniture Catalog',
    }
    return render(request, 'store/catalog.html', context)


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related = list(Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4])
    if len(related) < 4:
        others = list(Product.objects.exclude(pk=product.pk)[:8])
        for o in others:
            if o not in related and len(related) < 4:
                related.append(o)
    related_products = related[:4]
    reviews = product.reviews.all().order_by('-created_at')

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'page_title': 'Product Details',
    }
    return render(request, 'store/product_detail.html', context)


def search_view(request):
    query = request.GET.get('q', '').strip()
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

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
    wishlist_ids = request.session.get('glory_wishlist', [])
    products = Product.objects.filter(id__in=wishlist_ids)
    return render(request, 'store/wishlist.html', {'products': products})


def cart_view(request):
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
            product = get_object_or_404(Product, pk=product_id)

            cart = request.session.get('glory_cart', [])
            # Check if item exists in cart
            existing = next((item for item in cart if item['id'] == product.id and item.get('size') == size), None)
            if existing:
                existing['quantity'] += quantity
            else:
                cart.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'size': size,
                    'image': product.primary_image,
                    'material': product.material,
                })
            request.session['glory_cart'] = cart
            request.session.modified = True
            return JsonResponse({'status': 'success', 'cart_count': len(cart), 'cart': cart})
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
            return JsonResponse({'status': 'success', 'cart_count': len(cart), 'cart': cart})
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

