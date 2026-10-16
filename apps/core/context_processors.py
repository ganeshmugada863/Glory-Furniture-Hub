def global_furniture_context(request):
    """Provides global context to all Django templates for Glory Furniture Hub."""
    from apps.store.models import Category, Product
    try:
        categories = list(Category.objects.all().order_by('order', 'name'))
    except Exception:
        categories = []

    user = request.user if (hasattr(request, 'user') and request.user.is_authenticated) else None
    profile = getattr(user, 'profile', None) if user else None

    session = getattr(request, 'session', None) or {}

    if user:
        user_name = (profile.full_name if profile and profile.full_name else user.get_full_name()) or user.username
        user_email = user.email or ''
        user_phone = profile.phone if profile else ''
        current_role = profile.role if profile else ('admin' if (user.is_staff or user.is_superuser) else 'customer')
        cart = (profile.cart_items if profile and profile.cart_items is not None else None) or (session.get('glory_cart', []) if hasattr(session, 'get') else [])
        wishlist = (profile.wishlist_ids if profile and profile.wishlist_ids is not None else None) or (session.get('glory_wishlist', []) if hasattr(session, 'get') else [])
    else:
        current_role = session.get('glory_role', 'customer') if hasattr(session, 'get') else 'customer'
        user_name = session.get('glory_user_name', '') if hasattr(session, 'get') else ''
        user_email = session.get('glory_user_email', '') if hasattr(session, 'get') else ''
        user_phone = session.get('glory_user_phone', '') if hasattr(session, 'get') else ''
        cart = session.get('glory_cart', []) if hasattr(session, 'get') else []
        wishlist = session.get('glory_wishlist', []) if hasattr(session, 'get') else []

    cart_list = cart if isinstance(cart, list) else []
    wishlist_list = wishlist if isinstance(wishlist, list) else []

    wishlist_products = []
    if wishlist_list:
        try:
            clean_wishlist = [int(x) for x in wishlist_list if str(x).isdigit()]
            if clean_wishlist:
                prods = {p.id: p for p in Product.objects.filter(id__in=clean_wishlist).select_related('category')}
                wishlist_products = [prods[pid] for pid in clean_wishlist if pid in prods]
        except Exception:
            wishlist_products = []

    from apps.core.models import WebsiteSettings, HomeMediaCMS
    try:
        site_settings = WebsiteSettings.get_settings()
    except Exception:
        site_settings = None

    try:
        home_media_cms = HomeMediaCMS.get_cms()
    except Exception:
        home_media_cms = None

    try:
        from apps.core.models import FooterPage
        footer_pages = list(FooterPage.objects.filter(is_in_footer=True, is_published=True).order_by('footer_order', 'id'))
    except Exception:
        footer_pages = []

    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', 'https://gloryfurniturehub.com').rstrip('/')
    req_path = getattr(request, 'path', '/')
    canonical_url = f"{site_url}{req_path}"

    return {
        'SITE_URL': site_url,
        'CANONICAL_URL': canonical_url,
        'SITE_NAME': site_settings.website_name if site_settings else 'Glory Furniture Hub',
        'SITE_TAGLINE': (site_settings.tagline if site_settings and site_settings.tagline else 'Fine Teak Craftsmanship'),
        'WEBSITE_SETTINGS': site_settings,
        'HOME_MEDIA_CMS': home_media_cms,
        'FOOTER_PAGES': footer_pages,
        'GLOBAL_CATEGORIES': categories,
        'CURRENT_ROLE': current_role,
        'USER_NAME': user_name,
        'USER_EMAIL': user_email,
        'USER_PHONE': user_phone,
        'CART_ITEMS': cart_list,
        'CART_COUNT': len(cart_list),
        'WISHLIST_COUNT': len(wishlist_list),
        'WISHLIST_PRODUCTS': wishlist_products,
        'WISHLIST_IDS': wishlist_list,
    }

