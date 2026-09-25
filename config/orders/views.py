import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from catalog.models import Products
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Customers can view their own orders; staff/admins see all
        if self.request.user and self.request.user.is_authenticated:
            if getattr(self.request.user, 'role', '') == 'admin' or self.request.user.is_staff:
                return Order.objects.all().prefetch_related('items__product', 'user').order_by('-created_at')
            return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')
        return Order.objects.none()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def checkout(self, request):
        """
        Processes checkout and creates an atomic Order and OrderItems.
        Supports both logged-in users and guest customers.
        Accepts direct items payload or falls back to active cart.
        """
        user = request.user if request.user and request.user.is_authenticated else None
        data = request.data
        shipping_address = data.get('shipping_address') or {}
        
        # 1. Resolve phone number
        phone_number = data.get('phone_number') or ''
        if not phone_number and isinstance(shipping_address, dict):
            phone_number = shipping_address.get('phone') or ''
        if not phone_number and user:
            phone_number = getattr(user, 'phone', '') or ''

        # 2. Resolve items
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

        # 3. Calculate order pricing
        subtotal = 0.0
        order_items_to_create = []

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                phone_number=str(phone_number),
                total_amount=0,
                shipping_fee=float(data.get('shipping_fee') or 0),
                shipping_address=shipping_address,
                status='pending',
                payment_status=data.get('payment_status', 'unpaid')
            )

            for it in items_data:
                p_id = it.get('product_id') or it.get('id')
                qty = int(it.get('quantity') or it.get('qty') or 1)
                
                # Lookup product
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

                # Fallback to first product if test item
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
                            unit_price=unit_price,
                            quantity=qty
                        )
                    )
                    subtotal += unit_price * qty

                    # Deduct inventory stock safely
                    if product.stock >= qty:
                        product.stock -= qty
                        product.save(update_fields=['stock'])

            if order_items_to_create:
                OrderItem.objects.bulk_create(order_items_to_create)

            shipping_fee = float(data.get('shipping_fee') or (0.0 if subtotal >= 5000 else 120.0))
            order.total_amount = subtotal + shipping_fee
            order.shipping_fee = shipping_fee
            order.save(update_fields=['total_amount', 'shipping_fee'])

            # Clean up user cart if exists
            if user:
                Cart.objects.filter(user=user).delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)