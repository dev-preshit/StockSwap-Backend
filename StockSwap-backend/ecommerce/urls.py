from django.urls import path
from .views import (
    ProductListCreateView, ProductCategoryView, ProductDetailView,
    UserProductsView, CheckoutView, MySalesView, MyPurchasesView
)

urlpatterns = [
    path('product/', ProductListCreateView.as_view(), name='product-list-create'),
    path('product/category/<str:category>/', ProductCategoryView.as_view(), name='product-category'),
    path('product/user/<str:user>/', UserProductsView.as_view(), name='user-products'),
    path('product/checkout/', CheckoutView.as_view(), name='product-checkout'),
    path('product/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('purchase/', MySalesView.as_view(), name='my-sales'),
    path('purchase/user/', MyPurchasesView.as_view(), name='my-purchases'),
]
