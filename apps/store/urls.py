from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.catalog_view, name='catalog'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('search/', views.search_view, name='search'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('cart/', views.cart_view, name='cart'),
    path('api/cart/add/', views.cart_add_api, name='cart_add_api'),
    path('api/cart/remove/', views.cart_remove_api, name='cart_remove_api'),
    path('api/wishlist/toggle/', views.wishlist_toggle_api, name='wishlist_toggle_api'),
]
