from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_view, name='home'),
    path('welcome/', views.welcome_view, name='welcome'),
    path('home/', views.home_view, name='home_alt'),
    path('store/', views.home_view, name='store_home'),
    path('splash/', views.splash_view, name='splash'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('guide/', views.guide_view, name='guide'),
    path('api/switch-role/', views.switch_role_api, name='switch_role_api'),
    path('api/ai-chat/', views.ai_chat_api, name='ai_chat_api'),
    path('api/reverse-geocode/', views.reverse_geocode_api, name='reverse_geocode_api'),

    # Six Managed Footer & Policy Pages
    path('contact-us/', views.policy_page_view, {'slug': 'contact-us'}, name='contact_us'),
    path('terms-and-conditions/', views.policy_page_view, {'slug': 'terms-and-conditions'}, name='terms_and_conditions'),
    path('privacy-policy/', views.policy_page_view, {'slug': 'privacy-policy'}, name='privacy_policy'),
    path('refunds-cancellations/', views.policy_page_view, {'slug': 'refunds-cancellations'}, name='refunds_cancellations'),
    path('shipping-policy/', views.policy_page_view, {'slug': 'shipping-policy'}, name='shipping_policy'),
    path('payment-installment-policy/', views.policy_page_view, {'slug': 'payment-installment-policy'}, name='payment_installment_policy'),

    # Backward compatibility aliases
    path('terms/', views.policy_page_redirect, {'slug': 'terms-and-conditions'}),
    path('privacy/', views.policy_page_redirect, {'slug': 'privacy-policy'}),
    path('shipping/', views.policy_page_redirect, {'slug': 'shipping-policy'}),
    path('cancellations/', views.policy_page_redirect, {'slug': 'refunds-cancellations'}),
    path('policy/<slug:slug>/', views.policy_page_view, name='policy_page_generic'),
]

