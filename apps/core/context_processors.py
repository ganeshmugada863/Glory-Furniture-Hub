def global_furniture_context(request):
    """Provides global context to all Django templates for Glory Furniture Hub."""
    from apps.store.models import Category
    try:
        categories = Category.objects.all().order_by('order', 'name')
    except Exception:
        categories = []

    # Get active role from session, default to customer
    current_role = request.session.get('glory_role', 'customer')
    user_name = request.session.get('glory_user_name', 'Ganesh M.')
    user_email = request.session.get('glory_user_email', 'ganesh@example.com')
    user_phone = request.session.get('glory_user_phone', '+91 98765 43210')

    cart = request.session.get('glory_cart', [])
    wishlist = request.session.get('glory_wishlist', [])

    wishlist_products = []
    if wishlist:
        try:
            from apps.store.models import Product
            prods = {p.id: p for p in Product.objects.filter(id__in=wishlist).select_related('category')}
            wishlist_products = [prods[pid] for pid in wishlist if pid in prods]
        except Exception:
            wishlist_products = []

    return {
        'SITE_NAME': 'Glory Furniture Hub',
        'SITE_TAGLINE': 'Handcrafted Luxury Solid Wood Furniture',
        'GLOBAL_CATEGORIES': categories,
        'CURRENT_ROLE': current_role,
        'USER_NAME': user_name,
        'USER_EMAIL': user_email,
        'USER_PHONE': user_phone,
        'CART_COUNT': len(cart),
        'WISHLIST_COUNT': len(wishlist),
        'WISHLIST_PRODUCTS': wishlist_products,
        'WISHLIST_IDS': wishlist,
    }

