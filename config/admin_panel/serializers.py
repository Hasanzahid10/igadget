from rest_framework import serializers
from catalog.models import Category, Products, ProductsImage
from orders.models import Order, OrderItem


class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsImage
        fields = '__all__'


class AdminProductSerializer(serializers.ModelSerializer):
    images = AdminProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = (
            'id', 'title', 'slug', 'description', 'price',
            'discount_price', 'discount_percentage', 'category',
            'brand', 'is_featured', 'is_deal_of_the_day', 'images'
        )


class AdminCategorySerializer(serializers.ModelSerializer):
    icon_url= serializers.CharField(source='icon', allow_null=True, required=False)
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'icon_url', 'parent')
        extra_kwargs = {'slug':{'required':False}}


class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_title', 'unit_price', 'quantity', 'subtotal')


class AdminOrderSerializer(serializers.ModelSerializer):
    items = AdminOrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer_email', 'phone_number',
            'total_amount', 'shipping_fee', 'status', 'payment_status',
            'shipping_address', 'created_at', 'items'
        )