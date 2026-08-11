from rest_framework import serializers
from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    shop_name = serializers.SerializerMethodField()
    seller_username = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'price', 'quantity',
            'image', 'created_at', 'shop_name', 'seller_username', 'owner_id'
        ]
        read_only_fields = ['id', 'created_at', 'shop_name', 'seller_username', 'owner_id']

    def get_shop_name(self, obj):
        return obj.shop.shop_name if obj.shop else ''

    def get_seller_username(self, obj):
        return obj.shop.user.username if obj.shop and obj.shop.user else ''

    def get_owner_id(self, obj):
        return obj.shop.user.id if obj.shop and obj.shop.user else None

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        if obj.image_url:
            return obj.image_url
        return None

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'quantity', 'image', 'image_url']

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

class OrderSerializer(serializers.ModelSerializer):
    buyer_username = serializers.SerializerMethodField()
    buyer_shop_name = serializers.SerializerMethodField()
    seller_username = serializers.SerializerMethodField()
    seller_shop_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'product', 'product_name', 'buyer', 'buyer_username', 'buyer_shop_name',
            'seller', 'seller_username', 'seller_shop_name', 'quantity',
            'price_at_purchase', 'total_amount', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_buyer_username(self, obj):
        return obj.buyer.username if obj.buyer else ''

    def get_buyer_shop_name(self, obj):
        if hasattr(obj.buyer, 'shop'):
            return obj.buyer.shop.shop_name
        return ''

    def get_seller_username(self, obj):
        return obj.seller.username if obj.seller else ''

    def get_seller_shop_name(self, obj):
        if hasattr(obj.seller, 'shop'):
            return obj.seller.shop.shop_name
        return ''

class CheckoutSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
