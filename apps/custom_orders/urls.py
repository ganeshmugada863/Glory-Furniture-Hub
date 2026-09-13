from django.urls import path
from . import views

urlpatterns = [
    path('custom-request/', views.custom_request_view, name='custom_request'),
    path('custom-request-confirmation/', views.custom_confirmation_view, name='custom_request_confirmation'),
    path('profile/requests/', views.my_requests_view, name='my_requests'),
]
