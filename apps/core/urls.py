from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home_alt'),
    path('splash/', views.splash_view, name='splash'),
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('guide/', views.guide_view, name='guide'),
    path('api/switch-role/', views.switch_role_api, name='switch_role_api'),
    path('api/ai-chat/', views.ai_chat_api, name='ai_chat_api'),
    path('api/reverse-geocode/', views.reverse_geocode_api, name='reverse_geocode_api'),
]

