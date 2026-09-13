from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from apps.store.models import Product, Category

def home_view(request):
    # If session role is admin and they navigate to home, redirect to admin portal
    if request.session.get('glory_role') == 'admin':
        return redirect('admin_portal')

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


def guide_view(request):
    """Glory Furniture Comprehensive Customer, Quality, Care & Assembly Guide."""
    product_query = request.GET.get('product', '').strip()
    order_id = request.GET.get('order', '').strip()
    context = {
        'product_query': product_query,
        'order_id': order_id,
    }
    return render(request, 'core/guide.html', context)

