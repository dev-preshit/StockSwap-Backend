from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop', 'category', 'price', 'quantity', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description', 'shop__shop_name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'buyer', 'seller', 'quantity', 'price_at_purchase', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product_name', 'buyer__username', 'seller__username')
