from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        # Customers can only view their own orders; admins see all
        if getattr(self.request.user, 'role', '') == 'admin':
            return Order.objects.all().prefetch_related('items__product')
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Converts user's active cart into a confirmed order."""
        user = request.user
        shipping_address = request.data.get('shipping_address')

        if not shipping_address:
            return Response(
                {"error": "Shipping address is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Extract phone number directly from request, or fall back to user profile/address JSON
        phone_number = request.data.get('phone_number')
        if not phone_number and isinstance(shipping_address, dict):
            phone_number = shipping_address.get('phone')
        if not phone_number:
            phone_number = getattr(user, 'phone', None)

        if not phone_number:
            return Response(
                {"error": "Phone number is required for order confirmation calls."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Fetch active cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Calculate order pricing
        shipping_fee = 0.00 if cart.total_price >= 999 else 60.00
        total_amount = cart.total_price + shipping_fee

        # 4. Atomic database creation
        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                phone_number=phone_number,
                total_amount=total_amount,
                shipping_fee=shipping_fee,
                shipping_address=shipping_address,
                status='pending',  # Explicitly set to pending for call verification
                payment_status='unpaid'
            )

            # Convert CartItems to OrderItems
            for cart_item in cart.items.all():
                effective_price = (
                    cart_item.product.discount_price
                    if cart_item.product.discount_price
                    else cart_item.product.price
                )
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    unit_price=effective_price,
                    quantity=cart_item.quantity
                )

            # Clear active cart items
            cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)