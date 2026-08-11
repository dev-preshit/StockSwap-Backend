from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Product, Order
from .serializers import (
    ProductSerializer, ProductCreateUpdateSerializer,
    OrderSerializer, CheckoutSerializer
)

class ProductListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request):
        queryset = Product.objects.filter(quantity__gt=0)
        search_query = request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__icontains=search_query)
            )
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not hasattr(request.user, 'shop'):
            return Response({'detail': 'Logged in user does not have an active shop.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(shop=request.user.shop)
            out_serializer = ProductSerializer(product, context={'request': request})
            return Response(out_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductCategoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category):
        queryset = Product.objects.filter(category__iexact=category, quantity__gt=0)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.shop.user != request.user:
            return Response({'detail': 'You do not have permission to edit this product.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductCreateUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            out_serializer = ProductSerializer(updated_product, context={'request': request})
            return Response(out_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.shop.user != request.user:
            return Response({'detail': 'You do not have permission to delete this product.'}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({'detail': 'Product deleted successfully.'}, status=status.HTTP_200_OK)

class UserProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user):
        # Match user by username/email or user id
        target_user = None
        if user.isdigit():
            target_user = User.objects.filter(pk=int(user)).first()
        if not target_user:
            target_user = User.objects.filter(Q(username__iexact=user) | Q(email__iexact=user)).first()

        if not target_user or not hasattr(target_user, 'shop'):
            return Response([], status=status.HTTP_200_OK)

        # "My Listings" endpoint displays all products for the seller shop, including quantity 0
        products = Product.objects.filter(shop=target_user.shop)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            with transaction.atomic():
                # Lock row for atomic purchase check
                product = Product.objects.select_for_update().filter(pk=product_id).first()
                if not product:
                    return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

                # Check 1: User cannot buy their own product
                if product.shop.user == request.user:
                    return Response({'detail': 'A user cannot buy their own product.'}, status=status.HTTP_400_BAD_REQUEST)

                # Check 2: Available quantity
                if quantity > product.quantity:
                    return Response({'detail': f'Requested quantity ({quantity}) exceeds available stock ({product.quantity}).'}, status=status.HTTP_400_BAD_REQUEST)

                # Decrement stock
                product.quantity -= quantity
                product.save()

                # Calculate fields
                price_at_purchase = product.price
                total_amount = price_at_purchase * quantity

                # Create Order
                order = Order.objects.create(
                    product=product,
                    product_name=product.name,
                    buyer=request.user,
                    seller=product.shop.user,
                    quantity=quantity,
                    price_at_purchase=price_at_purchase,
                    total_amount=total_amount,
                    status='paid'
                )

                out_serializer = OrderSerializer(order, context={'request': request})
                return Response(out_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MySalesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Orders sold from logged-in user's shop
        sales = Order.objects.filter(seller=request.user)
        serializer = OrderSerializer(sales, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class MyPurchasesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Orders logged-in user has bought
        purchases = Order.objects.filter(buyer=request.user)
        serializer = OrderSerializer(purchases, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
