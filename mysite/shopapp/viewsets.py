# shopapp/viewsets.py

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(ModelViewSet):
    """API для продуктов"""
    queryset = Product.objects.filter(archived=False)
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']


class OrderViewSet(ModelViewSet):
    """API для заказов"""
    queryset = Order.objects.select_related('user').prefetch_related('products').all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['user', 'products']
    ordering_fields = ['id', 'created_at']