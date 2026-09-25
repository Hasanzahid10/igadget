import django_filters
from catalog.models import Products
from orders.models import Order

#====================================
# creating product filtering
#====================================
class ProductFilter(django_filters.FilterSet):
    #searching by name
    name = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    title =django_filters.CharFilter(field_name='title',lookup_expr='icontains')
    #searching by price

    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    # Category and brand filtering
    category_slug = django_filters.CharFilter(field_name='category_slug', lookup_expr='icontains')
    brand_slug =django_filters.CharFilter(field_name='brand_slug', lookup_expr='icontains')
    #promotional searching
    is_featuree = django_filters.BooleanFilter(field_name='is_featured', lookup_expr='exact')
    is_deal = django_filters.BooleanFilter(field_name='is_deal', lookup_expr='exact')

    class Meta:
        model = Products
        fields = ['title', 'slug', 'category', 'brand', 'price', 'is_featured', 'is_deal_of_the_day', 'is_active']



class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status',lookup_expr='exact')
    payment_status = django_filters.CharFilter(field_name='payment_status',lookup_expr='exact')
    phone= django_filters.CharFilter(field_name='phone',lookup_expr='icontains')
    created_at = django_filters.DateFilter(field_name='crated_at',lookup_expr='gte')
    created_by = django_filters.CharFilter(field_name='crated_by',lookup_expr='lte')

    class Meta:
        model= Order
        fields = ['status','payment_status','phone']
