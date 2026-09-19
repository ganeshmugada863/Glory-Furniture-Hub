from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomRequest

def custom_request_view(request):
    if request.method == 'POST':
        user_name = ''
        user_email = ''
        user_phone = ''
        if request.user.is_authenticated:
            user_name = getattr(getattr(request.user, 'profile', None), 'full_name', '') or request.user.get_full_name() or request.user.username
            user_email = request.user.email
            user_phone = getattr(getattr(request.user, 'profile', None), 'phone', '')

        name = request.POST.get('name') or user_name or request.session.get('glory_user_name', '')
        email = request.POST.get('email') or user_email or request.session.get('glory_user_email', '')
        phone = request.POST.get('phone') or user_phone or request.session.get('glory_user_phone', '')
        category = request.POST.get('category', 'Custom Cot / Wooden Bed')
        wood_type = request.POST.get('wood_type', 'Pure Grade-A Burma Teak')
        dimensions = request.POST.get('dimensions', '6x6 King Bed Frame')
        budget_range = request.POST.get('budget_range', '₹75,000 - ₹1,50,000')
        description = request.POST.get('description', '')
        reference_image = request.POST.get('reference_image', '').strip()

        # Handle uploaded photo from device gallery or camera capture
        uploaded_file = request.FILES.get('reference_photo')
        captured_data = request.POST.get('captured_photo_data', '').strip()

        if uploaded_file:
            from django.core.files.storage import default_storage
            import uuid
            ext = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'jpg'
            filename = f"custom_requests/{uuid.uuid4().hex[:10]}.{ext}"
            saved_path = default_storage.save(filename, uploaded_file)
            reference_image = default_storage.url(saved_path)
        elif captured_data and captured_data.startswith('data:image'):
            import base64
            import uuid
            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage
            try:
                format_prefix, imgstr = captured_data.split(';base64,')
                ext = 'jpg' if 'jpeg' in format_prefix else ('png' if 'png' in format_prefix else 'jpg')
                file_data = base64.b64decode(imgstr)
                filename = f"custom_requests/cam_{uuid.uuid4().hex[:10]}.{ext}"
                saved_path = default_storage.save(filename, ContentFile(file_data))
                reference_image = default_storage.url(saved_path)
            except Exception as e:
                print('Error saving camera snapshot:', e)

        custom_req = CustomRequest.objects.create(
            customer_name=name,
            email=email,
            phone=phone,
            category=category,
            wood_type=wood_type,
            dimensions=dimensions,
            budget_range=budget_range,
            description=description,
            reference_image=reference_image,
            status='Submitted'
        )
        request.session['last_custom_req_id'] = custom_req.request_id
        return redirect('custom_request_confirmation')

    categories = [
        'Custom Cot / Wooden Bed',
        'Handcrafted Sofa Set',
        'Architectural Dining Table',
        'Artisan Pooja Mandir',
        'Custom Dressing Table',
        'Carved Podimes / Diwan',
        'Complete Home Interior Suite'
    ]
    wood_types = [
        'Pure Grade-A Burma Teak',
        'Seasoned CP Teak Wood',
        'Solid Walnut & Teak',
        'Pure Rosewood / Sheesham'
    ]
    budgets = [
        '₹25,000 - ₹50,000',
        '₹50,000 - ₹1,00,000',
        '₹1,00,000 - ₹2,00,000',
        '₹2,00,000 - ₹5,00,000',
        '₹5,00,000+'
    ]

    context = {
        'categories': categories,
        'wood_types': wood_types,
        'budgets': budgets,
    }
    return render(request, 'custom_orders/custom_request.html', context)


def custom_confirmation_view(request):
    req_id = request.session.get('last_custom_req_id')
    user = request.user if request.user.is_authenticated else None
    email = (user.email if user else None) or request.session.get('glory_user_email')
    req = None
    if req_id:
        req = CustomRequest.objects.filter(request_id=req_id).first()
        if req and email and req.email.strip().lower() != email.strip().lower() and not (user and (user.is_staff or user.is_superuser)):
            req = None
    return render(request, 'custom_orders/custom_confirmation.html', {'custom_req': req})


def my_requests_view(request):
    user = request.user if request.user.is_authenticated else None
    email = (user.email if user else None) or request.session.get('glory_user_email')
    if email:
        requests = CustomRequest.objects.filter(email__iexact=email).order_by('-created_at')
    else:
        requests = CustomRequest.objects.none()
    return render(request, 'custom_orders/my_requests.html', {'requests': requests})
