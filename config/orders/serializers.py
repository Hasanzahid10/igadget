from rest_framework import serializers
from .models import Order, OrderItem, DeliverySetting
from catalog.serializers import ProductListSerializer


class DeliverySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverySetting
        fields = ('id', 'inside_dhaka_fee', 'outside_dhaka_fee', 'updated_at')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'unit_price', 'quantity', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    is_guest = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'tracking_token', 'user', 'is_guest',
            'customer_name', 'customer_email', 'customer_phone',
            'total_amount', 'shipping_fee', 'delivery_zone',
            'status', 'payment_status', 'shipping_address',
            'created_at', 'items'
        )
        read_only_fields = ('id', 'order_number', 'tracking_token', 'is_guest', 'total_amount', 'created_at')