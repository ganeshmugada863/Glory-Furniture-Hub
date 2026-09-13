from django.contrib import admin
from .models import Category, Product, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'room_type', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'room_type')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'in_stock', 'rating', 'featured', 'new_arrival')
    list_filter = ('category', 'in_stock', 'featured', 'new_arrival', 'style')
    search_fields = ('name', 'description', 'material')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('author', 'comment', 'product__name')
