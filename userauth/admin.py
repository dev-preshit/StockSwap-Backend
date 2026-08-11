from django.contrib import admin
from .models import Shop

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop_name', 'user', 'phone', 'created_at')
    search_fields = ('shop_name', 'user__username', 'user__email', 'phone')
    readonly_fields = ('created_at',)
