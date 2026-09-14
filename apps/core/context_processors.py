def global_furniture_context(request):
    """Provides global context to all Django templates for Glory Furniture Hub."""
    from apps.store.models import Category, Product
    try:
        categories = Category.objects.all().order_by('order', 'name')
    except Exception:
        categories = []

    user = request.user if request.user.is_authenticated else None
    profile = getattr(user, 'profile', None) if user else None

    if user:
        user_name = (profile.full_name if profile and profile.full_name else user.get_full_name()) or user.username
        user_email = user.email
        user_phone = profile.phone if profile else ''
        current_role = profile.role if profile else ('admin' if (user.is_staff or user.is_superuser) else 'customer')
        cart = (profile.cart_items if profile and profile.cart_items else None) or request.session.get('glory_cart', [])
        wishlist = (profile.wishlist_ids if profile and profile.wishlist_ids else None) or request.session.get('glory_wishlist', [])
    else:
        current_role = request.session.get('glory_role', 'customer')
        user_name = request.session.get('glory_user_name', '')
        user_email = request.session.get('glory_user_email', '')
        user_phone = request.session.get('glory_user_phone', '')
        cart = request.session.get('glory_cart', [])
        wishlist = request.session.get('glory_wishlist', [])

    wishlist_products = []
    if wishlist:
        try:
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
        'CART_ITEMS': cart,
        'CART_COUNT': len(cart),
        'WISHLIST_COUNT': len(wishlist),
        'WISHLIST_PRODUCTS': wishlist_products,
        'WISHLIST_IDS': wishlist,
    }

