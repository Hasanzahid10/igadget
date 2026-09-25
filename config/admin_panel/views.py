from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status,filters
from rest_framework.decorators import action
from rest_framework.response import Response
from catalog.models import Category, Products, ProductsImage
from orders.models import Order
from .permissions import IsAdminUserRole
from .serializers import (
    AdminCategorySerializer,
    AdminProductSerializer,
    AdminProductImageSerializer,
    AdminOrderSerializer
)
from catalog.filters import ProductFilter,OrderFilter

class AdminCategoryViewSet(viewsets.ModelViewSet):
    """CRUD operations for managing categories."""
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAdminUserRole]


class AdminProductViewSet(viewsets.ModelViewSet):
    """CRUD operations for managing products, prices, and discounts."""
    queryset = Products.objects.all().prefetch_related('images')
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filter_class = ProductFilter
    search_fields = ['title','description','price','discount_price']
    ordering_fields = ['price','discount_price','create_at','title','name']

    @action(detail=True, methods=['patch'])
    def update_price_and_discount(self, request, pk=None):
        """Dedicated action to update price or discount price directly."""
        product = self.get_object()
        price = request.data.get('price')
        discount_price = request.data.get('discount_price')

        if price is not None:
            product.price = price
        if discount_price is not None:
            product.discount_price = discount_price

        product.save()  # Triggers automatic discount_percentage calculation in save()
        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminProductImageViewSet(viewsets.ModelViewSet):
    """Manage product images (Add, update primary image, delete)."""
    queryset = ProductsImage.objects.all()
    serializer_class = AdminProductImageSerializer
    permission_classes = [IsAdminUserRole]


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """View order lists, review customer phone numbers, and confirm orders after call verification."""
    queryset = Order.objects.all().prefetch_related('items__product', 'user').order_by('-created_at')
    serializer_class = AdminOrderSerializer
    permission_classes = [IsAdminUserRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filter_class = OrderFilter
    search_fields = ['order_number', 'phone_number', 'user__email']
    ordering_fields = ['created_at','total_amount']

    @action(detail=True, methods=['post'])
    def confirm_by_call(self, request, pk=None):
        """Mark an order as 'processing' after confirming details over the phone."""
        order = self.get_object()
        order.status = 'processing'
        order.save()
        return Response({
            "message": f"Order {order.order_number} confirmed by phone call.",
            "status": order.status
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update shipping status (e.g. pending -> processing -> shipped -> delivered)."""
        order = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']

        if new_status not in valid_statuses:
            return Response({"error": "Invalid status option."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()
        return Response({
            "message": f"Order status updated to {new_status}.",
            "status": order.status
        }, status=status.HTTP_200_OK)