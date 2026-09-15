from rest_framework import serializers
from .models import Order, OrderItem
from catalog.serializers import ProductListSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'unit_price', 'quantity', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'phone_number', 'total_amount', 'shipping_fee',
            'status', 'payment_status', 'shipping_address',
            'created_at', 'items'
        )
        read_only_fields = ('id', 'order_number', 'total_amount', 'created_at')