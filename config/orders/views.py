import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from catalog.models import Products
from .serializers import OrderSerializer

import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem, DeliverySetting
from cart.models import Cart
from catalog.models import Products
from .serializers import OrderSerializer, DeliverySettingSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Admin / Staff see all orders
        if self.request.user and self.request.user.is_authenticated:
            if getattr(self.request.user, 'role', '') == 'admin' or self.request.user.is_staff:
                return Order.objects.all().prefetch_related('items__product', 'user').order_by('-created_at')
            return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')
        return Order.objects.none()

    @action(detail=False, methods=['get', 'post', 'put', 'patch'], permission_classes=[permissions.AllowAny])
    def delivery_settings(self, request):
        """Returns or updates the admin-configured delivery fees and settings."""
        settings_obj = DeliverySetting.get_settings()
        if request.method in ['POST', 'PUT', 'PATCH']:
            serializer = DeliverySettingSerializer(settings_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = DeliverySettingSerializer(settings_obj)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def track(self, request):
        """
        Allows guest users and customers to track their order status without logging in.
        Query params: order_number AND (token OR phone)
        """
        order_number = request.query_params.get('order_number') or request.query_params.get('order_id')
        token = request.query_params.get('token')
        phone = request.query_params.get('phone')

        if not order_number:
            return Response(
                {"error": "Please provide an order number (e.g., ORD-XXXXXXXX)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_qs = Order.objects.filter(order_number__iexact=order_number.strip())

        if token:
            order_qs = order_qs.filter(tracking_token=token.strip())
        elif phone:
            clean_phone = phone.strip()
            order_qs = order_qs.filter(customer_phone__icontains=clean_phone)
        elif not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Security token or phone number required for order tracking."},
                status=status.HTTP_403_FORBIDDEN
            )

        order = order_qs.prefetch_related('items__product').first()
        if not order:
            return Response(
                {"error": "Order not found. Please check your order number and tracking details."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def checkout(self, request):
        """
        Processes checkout and creates an atomic Order and OrderItems.
        Supports both logged-in users and guest customers.
        """
        user = request.user if request.user and request.user.is_authenticated else None
        data = request.data
        shipping_address = data.get('shipping_address') or {}

        # Customer Details (Supports Guest)
        customer_name = data.get('customer_name') or shipping_address.get('name') or (getattr(user, 'name', '') if user else '') or 'Guest Buyer'
        customer_email = data.get('customer_email') or shipping_address.get('email') or (getattr(user, 'email', '') if user else '') or ''
        customer_phone = data.get('customer_phone') or data.get('phone_number') or shipping_address.get('phone') or (getattr(user, 'phone', '') if user else '') or ''

        # Delivery Zone & Settings
        delivery_zone = data.get('delivery_zone') or shipping_address.get('delivery_zone') or 'inside_dhaka'
        d_settings = DeliverySetting.get_settings()

        # 1. Resolve Items
        items_data = data.get('items') or []
        if not items_data and user:
            cart = Cart.objects.filter(user=user).first()
            if cart and cart.items.exists():
                items_data = [
                    {
                        'product_id': item.product.id,
                        'name': item.product.title,
                        'quantity': item.quantity,
                        'price': float(item.product.discount_price if item.product.discount_price else item.product.price)
                    }
                    for item in cart.items.all()
                ]

        if not items_data:
            return Response(
                {"error": "No items provided for checkout."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Process Order & Items
        subtotal = 0.0
        order_items_to_create = []

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                customer_name=str(customer_name).strip(),
                customer_email=str(customer_email).strip(),
                customer_phone=str(customer_phone).strip(),
                delivery_zone=delivery_zone,
                total_amount=0,
                shipping_fee=0,
                shipping_address=shipping_address,
                status='pending',
                payment_status=data.get('payment_status', 'unpaid')
            )

            for it in items_data:
                p_id = it.get('product_id') or it.get('id')
                qty = int(it.get('quantity') or it.get('qty') or 1)

                product = None
                if p_id:
                    try:
                        product = Products.objects.filter(id=int(p_id)).first()
                    except (ValueError, TypeError):
                        pass

                if not product and it.get('name'):
                    product = Products.objects.filter(title__iexact=it['name']).first()
                if not product and it.get('title'):
                    product = Products.objects.filter(title__iexact=it['title']).first()
                if not product:
                    product = Products.objects.first()

                if product:
                    unit_price = float(
                        it.get('price') or
                        it.get('unit_price') or
                        (product.discount_price if product.discount_price else product.price) or
                        0
                    )
                    order_items_to_create.append(
                        OrderItem(
                            order=order,
                            product=product,
                            selected_color=str(it.get('selectedColor') or it.get('selected_color') or 'Standard'),
                            selected_storage=str(it.get('selectedStorage') or it.get('selected_storage') or 'Standard'),
                            unit_price=unit_price,
                            quantity=qty
                        )
                    )
                    subtotal += unit_price * qty

                    if product.stock >= qty:
                        product.stock -= qty
                        product.save(update_fields=['stock'])

            if order_items_to_create:
                OrderItem.objects.bulk_create(order_items_to_create)

            # Determine Shipping Fee based on admin delivery settings
            provided_shipping_fee = data.get('shipping_fee')
            if provided_shipping_fee is not None:
                shipping_fee = float(provided_shipping_fee)
            else:
                if delivery_zone == 'outside_dhaka':
                    shipping_fee = float(d_settings.outside_dhaka_fee)
                else:
                    shipping_fee = float(d_settings.inside_dhaka_fee)

            order.total_amount = subtotal + shipping_fee
            order.shipping_fee = shipping_fee
            order.save(update_fields=['total_amount', 'shipping_fee'])

            if user:
                Cart.objects.filter(user=user).delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)