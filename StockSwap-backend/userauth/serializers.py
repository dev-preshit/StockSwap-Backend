from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from .models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'shop_name', 'phone', 'address', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'shop']

    def get_name(self, obj):
        if obj.first_name:
            return obj.first_name
        return obj.username.split('@')[0] if '@' in obj.username else obj.username

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=6, required=True)
    shop_name = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=50, required=True)
    address = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_email(self, value):
        email_clean = value.strip().lower()
        if User.objects.filter(username__iexact=email_clean).exists() or User.objects.filter(email__iexact=email_clean).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return email_clean

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        name = validated_data['name']
        shop_name = validated_data['shop_name']
        phone = validated_data['phone']
        address = validated_data.get('address', '')

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            Shop.objects.create(
                user=user,
                shop_name=shop_name,
                phone=phone,
                address=address
            )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password', '')

        user = None
        # Try authenticating with username=email or searching by email
        user_obj = User.objects.filter(email__iexact=email).first() or User.objects.filter(username__iexact=email).first()
        if user_obj:
            user = authenticate(username=user_obj.username, password=password)

        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials. Please check your email and password."})

        attrs['user'] = user
        return attrs
