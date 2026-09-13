from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomRequest

def custom_request_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Ganesh M.')
        email = request.POST.get('email', 'ganesh@example.com')
        phone = request.POST.get('phone', '+91 98765 43210')
        category = request.POST.get('category', 'Custom Cot / Wooden Bed')
        wood_type = request.POST.get('wood_type', 'Pure Grade-A Burma Teak')
        dimensions = request.POST.get('dimensions', '6x6 King Bed Frame')
        budget_range = request.POST.get('budget_range', '₹75,000 - ₹1,50,000')
        description = request.POST.get('description', '')
        reference_image = request.POST.get('reference_image', '')

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
    req = CustomRequest.objects.filter(request_id=req_id).first() if req_id else CustomRequest.objects.first()
    return render(request, 'custom_orders/custom_confirmation.html', {'custom_req': req})


def my_requests_view(request):
    requests = CustomRequest.objects.all().order_by('-created_at')
    return render(request, 'custom_orders/my_requests.html', {'requests': requests})
