from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from apps.store.models import Product, Category
from apps.bookings.models import Order

def home_view(request):
    # If session role is admin and they navigate to home, redirect to admin dashboard
    if request.session.get('glory_role') == 'admin':
        return redirect('admin_dashboard')

    categories = Category.objects.all().order_by('order', 'name')
    featured_products = Product.objects.filter(featured=True)[:8]
    if not featured_products.exists():
        featured_products = Product.objects.all()[:8]

    # 5 Handcrafted Category Cards: Beds, Sofa, Dining, Dressing, Diwan Cot
    room_cards = [
        {
            'title': 'BEDS',
            'subtitle': 'Royal Burma Teak',
            'image': '/static/images/card_bed.jpg',
            'query': 'Cot / Wooden Bed',
            'tag': 'Featured Masterpiece',
            'bg_color': '#FAF5EE',
            'border_color': '#E8DAC9',
        },
        {
            'title': 'SOFA',
            'subtitle': 'Chesterfield & Luxury',
            'image': '/static/images/card_sofa.jpg',
            'query': 'Sofa Set',
            'tag': 'Featured Masterpiece',
            'bg_color': '#F8F3EC',
            'border_color': '#E5D6C5',
        },
        {
            'title': 'DINING',
            'subtitle': '6 & 8-Seater Sets',
            'image': '/static/images/card_dining.jpg',
            'query': 'Dining Table',
            'tag': 'Featured Masterpiece',
            'bg_color': '#FAF6F0',
            'border_color': '#EADBCE',
        },
        {
            'title': 'DRESSING',
            'subtitle': 'Artisan Mirror Consoles',
            'image': '/static/images/card_decor.jpg',
            'query': 'Dressing Table',
            'tag': 'Featured Masterpiece',
            'bg_color': '#F9F4EE',
            'border_color': '#E8D9CC',
        },
        {
            'title': 'DIWAN COT',
            'subtitle': 'Low Diwan Peeta Benches',
            'image': '/static/images/card_office.jpg',
            'query': 'Podimes',
            'tag': 'Featured Masterpiece',
            'bg_color': '#F6F1EA',
            'border_color': '#E5D6C6',
        },
    ]

    hero_slides = [
        {
            'id': 1,
            'image': '/static/images/hero_epoxy_teak.jpg',
            'line1': 'Elevate Your Home with',
            'line2': "Glory's Artisanal Teak",
            'line3': 'Furniture.',
            'description': 'Discover timeless pieces crafted with natural teak wood and vibrant epoxy resin.',
            'cta_text': 'Explore Collection',
            'cta_link': '/catalog/',
            'gradient': 'from-[#24140E]/95 via-[#3D2318]/70 to-[#5C3D2E]/25',
        },
        {
            'id': 2,
            'image': '/static/images/card_sofa.jpg',
            'line1': 'Handcrafted Luxury',
            'line2': 'Solid Teak Wood',
            'line3': 'Sofa Collections.',
            'description': 'Pure Grade-A teak framing with premium high-density velvet and ergonomic lumbar support.',
            'cta_text': 'View Sofa Sets',
            'cta_link': '/catalog/?category=Sofa%20Set',
            'gradient': 'from-[#1F1008]/95 via-[#3B1E12]/70 to-[#6E3C22]/25',
        },
        {
            'id': 3,
            'image': '/static/images/card_bed.jpg',
            'line1': 'Royal Teak Wood',
            'line2': 'Bedroom Essentials &',
            'line3': 'Canopy Cots.',
            'description': 'Masterfully carved posture-slat cots and canopy beds engineered for generational durability.',
            'cta_text': 'Explore Beds',
            'cta_link': '/catalog/?category=Cot%20%2F%20Wooden%20Bed',
            'gradient': 'from-[#2B1810]/95 via-[#4A2C1C]/70 to-[#8C532B]/25',
        },
        {
            'id': 4,
            'image': '/static/images/card_dining.jpg',
            'line1': 'Artisanal 6 & 8-Seater',
            'line2': 'Teak Dining Sets &',
            'line3': 'Crafted Benches.',
            'description': 'Traditional mortise-and-tenon craftsmanship with water-resistant food-safe natural honey finish.',
            'cta_text': 'View Dining Sets',
            'cta_link': '/catalog/?category=Dining%20Table',
            'gradient': 'from-[#1B110C]/95 via-[#342017]/70 to-[#633A24]/25',
        },
    ]

    all_products = Product.objects.all()

    context = {
        'room_cards': room_cards,
        'hero_slides': hero_slides,
        'all_products': all_products,
        'categories': categories,
        'is_home_page': True,
    }
    return render(request, 'core/home.html', context)


def splash_view(request):
    return render(request, 'core/splash.html')


def onboarding_view(request):
    return render(request, 'core/onboarding.html')


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    return render(request, 'core/contact.html')


def faq_view(request):
    return render(request, 'core/faq.html')


@csrf_exempt
def switch_role_api(request):
    """Role switching is disabled. Enforces strict Customer and Admin separation."""
    return JsonResponse({'status': 'error', 'message': 'Role switching disabled. Sign in via /login/ or /admin/login/.'}, status=403)


@csrf_exempt
def ai_chat_api(request):
    """Glory AI Wood Assistant consultation chatbot."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message', '').lower().strip()
        except Exception:
            message = ''

        reply = ""
        action = None

        if not message:
            reply = "Hello! I am Glory AI, your artisanal woodwork consultant. How can I assist you with custom teak furniture today?"
        elif 'cot' in message or 'bed' in message:
            reply = "Our Royal Teak Cots are hand-chiseled from Grade-A Burma teak with posture-slat support. We offer King (6x6 ft), Queen (5x6 ft), and custom sizes with 10-year anti-termite guarantee! Would you like to view our cot catalog or book a measurement visit?"
            action = {'label': 'View Teak Cots', 'url': '/catalog/?category=Cot%20%2F%20Wooden%20Bed'}
        elif 'sofa' in message:
            reply = "We craft Maharaja (3+1+1) and Chesterfield teak sofa sets with high-density 40-density foam and washable velvet upholstery. Delivered in 7-10 days across India!"
            action = {'label': 'View Sofa Sets', 'url': '/catalog/?category=Sofa%20Set'}
        elif 'dining' in message or 'table' in message:
            reply = "Our Heritage Teak Dining Tables come in 6-seater and 8-seater configurations with water-resistant food-safe polish and matching rattan teak chairs."
            action = {'label': 'Explore Dining Tables', 'url': '/catalog/?category=Dining%20Table'}
        elif 'book' in message or 'order' in message or 'buy' in message:
            reply = "You can browse our complete solid Burma teak collection online and order directly with doorstep white-glove delivery."
            action = {'label': 'Browse Catalog', 'url': '/catalog/'}
        elif 'custom' in message or 'design' in message:
            reply = "Have a specific architectural drawing or Pinterest design in mind? Share your dimensions and wood preference, and our master craftsmen will create a tailored quote for you."
            action = {'label': 'Submit Custom Request', 'url': '/custom-request/'}
        elif 'wood' in message or 'teak' in message or 'quality' in message:
            reply = "All Glory Furniture pieces are carved from 100% seasoned kiln-dried Burma and CP Teak Wood, naturally resistant to moisture, warping, and termites."
        elif 'delivery' in message or 'ship' in message:
            reply = "We provide doorstep white-glove assembly and delivery across Hyderabad and all major cities in India within 5-10 business days."
        else:
            reply = f"Thank you for asking about '{message}'. Our master carpenters in Hyderabad specialize in custom solid teak wood creations. Would you like to explore our handcrafted furniture catalog?"
            action = {'label': 'Explore Complete Catalog', 'url': '/catalog/'}

        return JsonResponse({
            'status': 'success',
            'reply': reply,
            'action': action
        })
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)


def get_ordinal_suffix(day):
    if 11 <= day <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_ordinal_date(dt):
    if not dt:
        return ''
    day = dt.day
    suffix = get_ordinal_suffix(day)
    return f"{dt.strftime('%a')}, {day}{suffix} {dt.strftime('%b')} '{dt.strftime('%y')}"


def format_time_only(dt):
    if not dt:
        return ''
    t = dt.strftime("%I:%M%p").lower()
    if t.startswith('0'):
        t = t[1:]
    return t


def format_datetime_stamp(dt):
    if not dt:
        return ''
    return f"{format_ordinal_date(dt)} - {format_time_only(dt)}"


def build_guide_timeline(order=None, product_query=''):
    stage_keys = ['CONFIRMED', 'IN_PRODUCTION', 'SHIPPED', 'OUT_FOR_DELIVERY', 'DELIVERED']

    current_status = getattr(order, 'fulfillment_status', 'SHIPPED') if order else 'SHIPPED'
    if current_status in stage_keys:
        active_idx = stage_keys.index(current_status)
    else:
        active_idx = 2  # Default to SHIPPED

    t0 = (order.created_at if order and order.created_at else timezone.now()) - timedelta(days=6)

    history_map = {}
    if order:
        try:
            for h in order.status_history.all():
                history_map[h.fulfillment_status] = h.created_at
        except Exception:
            pass

    stages = []

    # 1. CONFIRMED
    idx = 0
    dt_c = history_map.get('CONFIRMED') or (order.created_at if order and order.created_at else t0)
    is_completed = (idx <= active_idx)
    is_current = (idx == active_idx)
    is_upcoming = (idx > active_idx)
    next_is_active_or_done = (idx + 1 <= active_idx)

    stages.append({
        'key': 'CONFIRMED',
        'title': 'Order Confirmed',
        'date_header': format_ordinal_date(dt_c),
        'is_completed': is_completed,
        'is_current': is_current,
        'is_upcoming': is_upcoming,
        'has_next_line': True,
        'line_is_active': next_is_active_or_done,
        'sub_events': [
            {'text': 'Your Order has been placed.', 'timestamp': format_datetime_stamp(dt_c)},
            {'text': 'Workshop has processed your order.', 'timestamp': format_datetime_stamp(dt_c + timedelta(days=2, hours=12, minutes=48))},
            {'text': 'Grade-A Burma Teak seasoned & selected by artisan.', 'timestamp': format_datetime_stamp(dt_c + timedelta(days=2, hours=14, minutes=41))},
        ],
        'nested_logs': [],
        'note': None,
    })

    # 2. IN_PRODUCTION
    idx = 1
    dt_p = history_map.get('IN_PRODUCTION') or (dt_c + timedelta(days=2))
    is_completed = (idx <= active_idx)
    is_current = (idx == active_idx)
    is_upcoming = (idx > active_idx)
    next_is_active_or_done = (idx + 1 <= active_idx)

    prod_sub_events = []
    prod_nested_logs = []
    prod_note = None
    if is_completed or is_current:
        prod_sub_events.append({'text': 'Master carpentry & joinery in progress.', 'timestamp': format_datetime_stamp(dt_p)})
        if is_current:
            prod_nested_logs = [
                {'text': 'Mortise-and-tenon structural framing assembled', 'timestamp': format_datetime_stamp(dt_p + timedelta(hours=1, minutes=2)) + ' - HYDERABAD WORKSHOP'},
                {'text': 'Precision hand-sanding & surface grain inspection', 'timestamp': format_datetime_stamp(dt_p + timedelta(hours=5, minutes=8)) + ' - HYDERABAD WORKSHOP'},
            ]
            prod_note = 'Carpentry checkpoint verified. Natural teak buffing underway.'
    else:
        prod_sub_events.append({'text': 'Item yet to enter production workshop.', 'timestamp': ''})

    stages.append({
        'key': 'IN_PRODUCTION',
        'title': 'In Production',
        'date_header': format_ordinal_date(dt_p) if (is_completed or is_current) else '',
        'is_completed': is_completed,
        'is_current': is_current,
        'is_upcoming': is_upcoming,
        'has_next_line': True,
        'line_is_active': next_is_active_or_done,
        'sub_events': prod_sub_events,
        'nested_logs': prod_nested_logs,
        'note': prod_note,
    })

    # 3. SHIPPED
    idx = 2
    dt_s = history_map.get('SHIPPED') or (dt_c + timedelta(days=3))
    is_completed = (idx <= active_idx)
    is_current = (idx == active_idx)
    is_upcoming = (idx > active_idx)
    next_is_active_or_done = (idx + 1 <= active_idx)

    ship_sub_events = []
    ship_nested_logs = []
    ship_note = None
    if is_completed or is_current:
        ship_sub_events.append({'text': 'Specialized Furniture Transport Fleet', 'timestamp': ''})
        ship_sub_events.append({'text': 'Your item has been securely dispatched.', 'timestamp': format_datetime_stamp(dt_s + timedelta(minutes=4))})
        if is_current:
            ship_nested_logs = [
                {'text': 'Your item has arrived at Central Dispatch Facility', 'timestamp': format_datetime_stamp(dt_s) + ' - HYDERABAD'},
                {'text': 'Multi-layer corner and foam packaging inspected', 'timestamp': format_datetime_stamp(dt_s + timedelta(minutes=2)) + ' - HYDERABAD'},
                {'text': 'Your item has departed Central Dispatch Facility', 'timestamp': format_datetime_stamp(dt_s + timedelta(hours=4, minutes=4)) + ' - HYDERABAD'},
            ]
            ship_note = 'Item in transit to regional distribution hub nearest to you.'
    else:
        ship_sub_events.append({'text': 'Item yet to be shipped.', 'timestamp': ''})

    stages.append({
        'key': 'SHIPPED',
        'title': 'Shipped',
        'date_header': format_ordinal_date(dt_s) if (is_completed or is_current) else '',
        'is_completed': is_completed,
        'is_current': is_current,
        'is_upcoming': is_upcoming,
        'has_next_line': True,
        'line_is_active': next_is_active_or_done,
        'sub_events': ship_sub_events,
        'nested_logs': ship_nested_logs,
        'note': ship_note,
    })

    # 4. OUT_FOR_DELIVERY
    idx = 3
    dt_o = history_map.get('OUT_FOR_DELIVERY') or (dt_c + timedelta(days=6))
    is_completed = (idx <= active_idx)
    is_current = (idx == active_idx)
    is_upcoming = (idx > active_idx)
    next_is_active_or_done = (idx + 1 <= active_idx)

    out_sub_events = []
    out_nested_logs = []
    out_note = None
    if is_completed or is_current:
        out_sub_events.append({'text': 'Item loaded onto local delivery vehicle.', 'timestamp': format_datetime_stamp(dt_o)})
        out_sub_events.append({'text': 'White-glove doorstep delivery crew en route.', 'timestamp': format_datetime_stamp(dt_o + timedelta(hours=1))})
        if is_current:
            out_note = 'Delivery partner will contact before arrival.'
    else:
        out_sub_events.append({'text': 'Item yet to be delivered.', 'timestamp': ''})

    stages.append({
        'key': 'OUT_FOR_DELIVERY',
        'title': 'Out For Delivery',
        'date_header': format_ordinal_date(dt_o) if (is_completed or is_current) else '',
        'is_completed': is_completed,
        'is_current': is_current,
        'is_upcoming': is_upcoming,
        'has_next_line': True,
        'line_is_active': next_is_active_or_done,
        'sub_events': out_sub_events,
        'nested_logs': out_nested_logs,
        'note': out_note,
    })

    # 5. DELIVERED
    idx = 4
    dt_d = history_map.get('DELIVERED') or (dt_c + timedelta(days=9))
    is_completed = (idx <= active_idx)
    is_current = (idx == active_idx)
    is_upcoming = (idx > active_idx)

    del_sub_events = []
    if is_completed or is_current:
        del_title = f"Delivered {format_ordinal_date(dt_d)}"
        del_sub_events.append({'text': 'Item delivered to room of choice.', 'timestamp': format_datetime_stamp(dt_d)})
        del_sub_events.append({'text': 'Assembly inspected & 10-year teak warranty certificate handed over.', 'timestamp': ''})
    else:
        del_title = f"Delivery Expected By {format_ordinal_date(dt_d)}"
        del_sub_events.append({'text': 'Item yet to be delivered.', 'timestamp': ''})
        del_sub_events.append({'text': f"Expected by {format_ordinal_date(dt_d)}", 'timestamp': ''})

    stages.append({
        'key': 'DELIVERED',
        'title': del_title,
        'date_header': '',
        'is_completed': is_completed,
        'is_current': is_current,
        'is_upcoming': is_upcoming,
        'has_next_line': False,
        'line_is_active': False,
        'sub_events': del_sub_events,
        'nested_logs': [],
        'note': None,
    })

    return stages


def guide_view(request):
    """
    Furniture Owner's Guide:
    Renders the vertical animated tracking timeline structure for the handcrafted furniture journey.
    """
    product_query = request.GET.get('product', '').strip()
    order_id = request.GET.get('order', '').strip()

    order = None
    if order_id:
        try:
            if order_id.isdigit():
                order = Order.objects.filter(Q(id=int(order_id)) | Q(order_number=order_id)).first()
            else:
                order = Order.objects.filter(
                    Q(order_number=order_id) | Q(booking__booking_id=order_id)
                ).first()
        except Exception:
            pass

    user = getattr(request, 'user', None)
    if not order and user and getattr(user, 'is_authenticated', False):
        order = Order.objects.filter(user=user).first()

    if not order:
        session = getattr(request, 'session', None)
        session_email = session.get('glory_user_email') if session else None
        if session_email:
            order = Order.objects.filter(email__iexact=session_email).first()

    if not order:
        order = Order.objects.first()

    timeline = build_guide_timeline(order, product_query=product_query)

    context = {
        'product_query': product_query or (order.product_name if order else 'Solid Burma Teak Masterpiece'),
        'order': order,
        'timeline': timeline,
    }
    return render(request, 'core/guide.html', context)


def reverse_geocode_api(request):
    """
    Reverse geocodes lat/lon into street address, city, state, pincode
    to support HTML5 Geolocation permission auto-fill.
    """
    lat = request.GET.get('lat', '').strip()
    lon = request.GET.get('lon', '').strip()

    if not lat or not lon:
        return JsonResponse({'status': 'error', 'message': 'Latitude and Longitude are required'}, status=400)

    try:
        import urllib.request
        import json

        url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}&addressdetails=1"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'GloryFurnitureHub/1.0 (contact@gloryfurniture.com)'
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            address = data.get('address', {})

            # Comprehensive rural & urban address parsing for India
            village_or_locality = (
                address.get('village') or
                address.get('hamlet') or
                address.get('suburb') or
                address.get('neighbourhood') or
                address.get('residential') or
                ''
            )
            road = address.get('road') or address.get('pedestrian') or address.get('footway') or ''
            mandal_or_taluk = address.get('subdistrict') or address.get('county') or address.get('tehsil') or ''
            district = address.get('state_district') or address.get('district') or ''
            
            street_parts = []
            if road:
                street_parts.append(road)
            if village_or_locality and village_or_locality not in street_parts:
                street_parts.append(village_or_locality)
            if mandal_or_taluk and mandal_or_taluk not in street_parts:
                street_parts.append(f"Mandal: {mandal_or_taluk}")
            
            street = ", ".join(street_parts) if street_parts else (district or '')
            flat = address.get('house_number') or address.get('building') or ''
            city = (
                address.get('city') or
                address.get('town') or
                address.get('municipality') or
                district or
                mandal_or_taluk or
                village_or_locality or
                'Hyderabad'
            )
            state = address.get('state') or 'Telangana'
            pincode = address.get('postcode') or ''

            return JsonResponse({
                'status': 'success',
                'data': {
                    'flat': flat,
                    'street': street,
                    'city': city,
                    'state': state,
                    'pincode': pincode,
                    'display_name': data.get('display_name', ''),
                    'suburb': address.get('suburb') or village_or_locality or mandal_or_taluk or '',
                    'district': district,
                    'village': address.get('village', ''),
                    'mandal': mandal_or_taluk,
                }
            })
    except Exception as e:
        # Graceful fallback: return partial coords with default Hyderabad state
        return JsonResponse({
            'status': 'partial',
            'data': {
                'flat': '',
                'street': '',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'pincode': '',
                'display_name': f"Coordinates: {lat}, {lon}",
                'error': str(e)
            }
        })


