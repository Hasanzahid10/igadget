from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Products
from .filters import ProductFilter
from .serializers import (
    CategorySerializer,
    BrandSerializer,
    ProductListSerializer,
    ProductDetailSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'slug', 'icon']
    filterset_fields = ['name', 'slug']
    ordering_fields = ['name', 'slug']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'slug']
    filterset_fields = ['name', 'slug']
    ordering_fields = ['name', 'slug']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


#==================================================================
# Products ViewSet
#==================================================================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.filter(is_active=True).prefetch_related('images').select_related('category', 'brand')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filter_class = ProductFilter
    search_fields = ['title', 'description', 'slug']
    filterset_fields = ['title', 'slug', 'category', 'brand', 'price', 'is_featured', 'is_deal_of_the_day']
    ordering_fields = ['price', 'create_at', 'title']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        """
        Supports retrieving a product by ID (e.g. /api/catalog/products/1/)
        or by slug (e.g. /api/catalog/products/iphone-15-pro/).
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)

        if lookup_value.isdigit():
            filter_kwargs = {'pk': int(lookup_value)}
        else:
            filter_kwargs = {'slug': lookup_value}

        obj = queryset.filter(**filter_kwargs).first()
        if not obj:
            raise NotFound(detail=f"Product with ID or slug '{lookup_value}' not found.")

        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    @action(detail=False, methods=['get'], url_path='featured', permission_classes=[IsAuthenticatedOrReadOnly])
    def featured(self, request):
        feature_products = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(feature_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='feature', permission_classes=[IsAuthenticatedOrReadOnly])
    def feature(self, request):
        return self.featured(request)

    @action(detail=False, methods=['get'], url_path='deals-of-the-day', permission_classes=[IsAuthenticatedOrReadOnly])
    def deals_of_the_day_hyphen(self, request):
        return self.deals_of_the_day(request)

    @action(detail=False, methods=['get'], url_path='deals_of_the_day', permission_classes=[IsAuthenticatedOrReadOnly])
    def deals_of_the_day(self, request):
        deals = self.get_queryset().filter(is_deal_of_the_day=True)
        serializer = self.get_serializer(deals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
