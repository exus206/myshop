# shopapp/serializers.py

from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discount',
            'quantity', 'created_at', 'in_stock', 'archived',
            'category', 'created_by'
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'delivery_address', 'promocode',
            'created_at', 'user', 'products'
        ]